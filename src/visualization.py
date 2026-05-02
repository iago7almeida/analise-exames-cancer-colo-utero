"""
Módulo de visualizações interativas com Plotly.
Cada função gera um gráfico e salva como HTML em output/.
"""
import os
import json
import urllib.request

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.config import DATA_DIR, OUTPUT_DIR, CORES, PALETA_REGIOES


def _salvar(fig, nome: str):
    """Salva figura Plotly como HTML interativo."""
    path = os.path.join(OUTPUT_DIR, f'{nome}.html')
    fig.write_html(path, include_plotlyjs='cdn')
    print(f"  ✅ Salvo: {path}")


def _layout_base(fig, title: str, height: int = 550):
    """Aplica layout padrão dark."""
    fig.update_layout(
        title=title, height=height,
        paper_bgcolor=CORES['fundo'], plot_bgcolor=CORES['plot_bg'],
        font_color=CORES['texto'], title_font_size=16,
    )


def _carregar_geojson():
    """Baixa e carrega GeoJSON dos estados brasileiros."""
    path = os.path.join(DATA_DIR, 'brazil_states.json')
    if not os.path.exists(path):
        print("  📥 Baixando GeoJSON...")
        url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
        urllib.request.urlretrieve(url, path)
    with open(path) as f:
        geo = json.load(f)
    for feat in geo['features']:
        feat['id'] = feat['properties'].get('sigla', '')
    return geo


# ==============================================================================
# GRÁFICOS EDA
# ==============================================================================

def grafico_mapa_coropletico(df: pd.DataFrame):
    """1. Mapa coroplético animado: mortalidade por UF ao longo dos anos."""
    print("🗺️  [1/12] Mapa Coroplético...")
    geo = _carregar_geojson()

    fig = px.choropleth(
        df, geojson=geo, locations='sigla_uf', color='taxa_mortalidade',
        animation_frame='ano', color_continuous_scale='YlOrRd',
        range_color=[0, df['taxa_mortalidade'].quantile(0.95)],
        scope='south america', hover_name='uf_nome',
        hover_data={'taxa_mortalidade': ':.2f', 'obitos': ':,.0f', 'sigla_uf': False},
        labels={'taxa_mortalidade': 'Mortalidade/100k', 'ano': 'Ano'},
        title='🗺️ Taxa de Mortalidade por Câncer de Colo do Útero — Brasil'
    )
    fig.update_geos(fitbounds="locations", visible=False, bgcolor='rgba(0,0,0,0)')
    _layout_base(fig, fig.layout.title.text, 650)
    fig.update_layout(margin=dict(l=0, r=0, t=60, b=0))
    _salvar(fig, '01_mapa_coropletico')


def grafico_serie_temporal(df: pd.DataFrame):
    """2. Série temporal da mortalidade nacional."""
    print("📈 [2/12] Série Temporal...")
    df_br = df.groupby('ano').agg(obt=('obitos', 'sum'), pop=('populacao', 'sum')).reset_index()
    df_br['taxa'] = (df_br['obt'] / df_br['pop']) * 100000
    df_br['mm3'] = df_br['taxa'].rolling(3, center=True).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_br['ano'], y=df_br['taxa'], mode='lines+markers',
                             name='Taxa Nacional', line=dict(color=CORES['primaria'], width=3),
                             marker=dict(size=8)))
    fig.add_trace(go.Scatter(x=df_br['ano'], y=df_br['mm3'], mode='lines',
                             name='Média Móvel (3a)', line=dict(color=CORES['secundaria'], width=2, dash='dash')))
    fig.add_vrect(x0=2019.5, x1=2021.5, fillcolor=CORES['alerta'], opacity=0.15,
                  annotation_text="COVID-19", annotation_position="top left")
    _layout_base(fig, '📈 Evolução da Taxa de Mortalidade — Brasil', 500)
    fig.update_layout(hovermode='x unified', legend=dict(orientation='h', y=1.02),
                      xaxis_title='Ano', yaxis_title='Óbitos por 100k mulheres')
    _salvar(fig, '02_serie_temporal')


def grafico_bar_race(df: pd.DataFrame):
    """3. Top 10 UFs animado por ano."""
    print("🏆 [3/12] Bar Chart Race...")
    df_s = df.sort_values(['ano', 'taxa_mortalidade'], ascending=[True, False])
    df_top = df_s.groupby('ano').head(10).reset_index(drop=True)

    fig = px.bar(df_top, x='taxa_mortalidade', y='sigla_uf', color='regiao',
                 animation_frame='ano', orientation='h',
                 color_discrete_map=PALETA_REGIOES, hover_name='uf_nome',
                 labels={'taxa_mortalidade': 'Mortalidade/100k', 'sigla_uf': 'Estado'},
                 title='🏆 Top 10 Estados com Maior Mortalidade')
    _layout_base(fig, fig.layout.title.text)
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, legend_title='Região')
    _salvar(fig, '03_bar_race')


def grafico_scatter_cobertura(df: pd.DataFrame):
    """4. Bubble chart: Cobertura vs Mortalidade."""
    print("🔬 [4/12] Scatter Cobertura vs Mortalidade...")
    df_s = df[df['ano'].between(2014, 2022)].groupby(
        ['uf_nome', 'sigla_uf', 'regiao']
    ).agg(cob=('razao_exames_pop', 'mean'), mort=('taxa_mortalidade', 'mean'),
          pop=('populacao', 'mean'), obt=('obitos', 'sum')).reset_index()

    fig = px.scatter(df_s, x='cob', y='mort', size='pop', color='regiao',
                     hover_name='uf_nome', size_max=50, trendline='ols',
                     color_discrete_map=PALETA_REGIOES,
                     labels={'cob': 'Cobertura (%)', 'mort': 'Mortalidade/100k'},
                     title='🔬 Cobertura de Rastreamento vs. Mortalidade (2014-2022)')
    for _, row in df_s.iterrows():
        fig.add_annotation(x=row['cob'], y=row['mort'], text=row['sigla_uf'],
                           showarrow=False, font=dict(size=9, color=CORES['texto']), yshift=12)
    _layout_base(fig, fig.layout.title.text, 600)
    _salvar(fig, '04_scatter_cobertura')


def grafico_heatmap_temporal(df: pd.DataFrame):
    """5. Heatmap UF × Ano."""
    print("🌡️  [5/12] Heatmap Temporal...")
    pivot = df.pivot_table(values='taxa_mortalidade', index='sigla_uf', columns='ano').fillna(0)
    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]

    fig = px.imshow(pivot, color_continuous_scale='YlOrRd', aspect='auto',
                    labels={'x': 'Ano', 'y': 'Estado', 'color': 'Mortalidade/100k'},
                    title='🌡️ Heatmap: Mortalidade por Estado e Ano')
    _layout_base(fig, fig.layout.title.text, 750)
    _salvar(fig, '05_heatmap_temporal')


def grafico_sunburst(df: pd.DataFrame):
    """6. Sunburst: Região → Estado → Óbitos."""
    print("🌐 [6/12] Sunburst...")
    ult = df['ano'].max()
    df_s = df[df['ano'] == ult][['regiao', 'uf_nome', 'obitos', 'taxa_mortalidade']].copy()
    df_s = df_s[df_s['regiao'] != 'Outros']

    fig = px.sunburst(df_s, path=['regiao', 'uf_nome'], values='obitos',
                      color='taxa_mortalidade', color_continuous_scale='YlOrRd',
                      title=f'🌐 Distribuição de Óbitos por Região e Estado ({ult})')
    _layout_base(fig, fig.layout.title.text, 600)
    _salvar(fig, '06_sunburst')


def grafico_treemap(df: pd.DataFrame):
    """7. Treemap proporcional."""
    print("🌳 [7/12] Treemap...")
    df_t = df.groupby(['regiao', 'uf_nome']).agg(
        obt=('obitos', 'sum'), mort=('taxa_mortalidade', 'mean')).reset_index()
    df_t = df_t[df_t['regiao'] != 'Outros']

    fig = px.treemap(df_t, path=[px.Constant("Brasil"), 'regiao', 'uf_nome'],
                     values='obt', color='mort', color_continuous_scale='YlOrRd',
                     title='🌳 Treemap: Óbitos Acumulados por Região e Estado')
    _layout_base(fig, fig.layout.title.text, 600)
    _salvar(fig, '07_treemap')


def grafico_boxplot_regional(df: pd.DataFrame):
    """8. Boxplot dual por região."""
    print("📊 [8/12] Boxplot Regional...")
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=['Mortalidade/100k', 'Cobertura (%)'])
    for reg, cor in PALETA_REGIOES.items():
        dr = df[df['regiao'] == reg]
        fig.add_trace(go.Box(y=dr['taxa_mortalidade'], name=reg, marker_color=cor,
                             boxmean='sd', showlegend=True), row=1, col=1)
        fig.add_trace(go.Box(y=dr['razao_exames_pop'], name=reg, marker_color=cor,
                             boxmean='sd', showlegend=False), row=1, col=2)
    _layout_base(fig, '📊 Distribuição por Região', 500)
    fig.update_layout(legend=dict(orientation='h', y=1.05))
    _salvar(fig, '08_boxplot_regional')


def grafico_painel_multi(df: pd.DataFrame):
    """9. Painel multi-métrico (3 painéis)."""
    print("📊 [9/12] Painel Multi-Métrico...")
    df_br = df.groupby('ano').agg(ex=('exames_realizados','sum'), pop=('populacao','sum'),
                                   dg=('diagnosticos_positivos','sum'), ob=('obitos','sum')).reset_index()
    df_br['cob'] = (df_br['ex'] / df_br['pop']) * 100
    df_br['pos'] = (df_br['dg'] / df_br['ex']) * 100
    df_br['mort'] = (df_br['ob'] / df_br['pop']) * 100000

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        subplot_titles=['Cobertura (%)', 'Positividade (%)', 'Mortalidade/100k'])
    fig.add_trace(go.Scatter(x=df_br['ano'], y=df_br['cob'], mode='lines+markers',
                             line=dict(color=CORES['terciaria'], width=3), name='Cobertura'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_br['ano'], y=df_br['pos'], mode='lines+markers',
                             line=dict(color=CORES['alerta'], width=3), name='Positividade'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_br['ano'], y=df_br['mort'], mode='lines+markers',
                             line=dict(color=CORES['primaria'], width=3), name='Mortalidade'), row=3, col=1)
    _layout_base(fig, '📊 Panorama Nacional', 700)
    fig.update_layout(showlegend=False, hovermode='x unified')
    _salvar(fig, '09_painel_multi')


def grafico_funil(df: pd.DataFrame):
    """10. Funil de rastreamento."""
    print("🔻 [10/12] Funil...")
    ult = df['ano'].max()
    d = df[df['ano'] == ult]
    etapas = ['População Alvo', 'Examinadas', 'Diagnósticos+', 'Óbitos']
    vals = [d['populacao'].sum(), d['exames_realizados'].sum(),
            d['diagnosticos_positivos'].sum(), d['obitos'].sum()]

    fig = go.Figure(go.Funnel(
        y=etapas, x=vals, textinfo='value+percent initial',
        marker=dict(color=[CORES['secundaria'], CORES['terciaria'], CORES['alerta'], CORES['primaria']]),
    ))
    _layout_base(fig, f'🔻 Funil do Rastreamento ({ult})', 450)
    _salvar(fig, '10_funil')


def grafico_small_multiples(df: pd.DataFrame):
    """11. Small multiples por região."""
    print("📈 [11/12] Small Multiples...")
    dr = df[df['regiao'] != 'Outros'].groupby(['ano','regiao']).agg(
        ob=('obitos','sum'), pop=('populacao','sum')).reset_index()
    dr['taxa'] = (dr['ob'] / dr['pop']) * 100000

    fig = px.line(dr, x='ano', y='taxa', color='regiao', facet_col='regiao', facet_col_wrap=3,
                  color_discrete_map=PALETA_REGIOES, markers=True,
                  labels={'taxa': 'Mortalidade/100k', 'ano': 'Ano'},
                  title='📈 Evolução da Mortalidade por Região')
    _layout_base(fig, fig.layout.title.text, 500)
    fig.update_layout(showlegend=False)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
    _salvar(fig, '11_small_multiples')


def grafico_radar(df: pd.DataFrame):
    """12. Radar chart por região."""
    print("🕸️  [12/12] Radar Chart...")
    dr = df[df['regiao'] != 'Outros'].groupby('regiao').agg(
        mort=('taxa_mortalidade','mean'), cob=('razao_exames_pop','mean'),
        pos=('taxa_positividade','mean'), vac=('cobertura_vacinal_100k','mean')).reset_index()

    for c in ['mort','cob','pos','vac']:
        mx = dr[c].max()
        dr[c + '_n'] = dr[c] / mx if mx > 0 else 0

    cats = ['Mortalidade', 'Cobertura', 'Positividade', 'Vacinal']
    fig = go.Figure()
    for _, row in dr.iterrows():
        vals = [row['mort_n'], row['cob_n'], row['pos_n'], row['vac_n'], row['mort_n']]
        fig.add_trace(go.Scatterpolar(r=vals, theta=cats + [cats[0]], fill='toself',
                                       name=row['regiao'], line_color=PALETA_REGIOES.get(row['regiao'],'#888'),
                                       opacity=0.7))
    _layout_base(fig, '🕸️ Perfil Multidimensional por Região', 550)
    fig.update_layout(
        polar=dict(bgcolor=CORES['plot_bg'],
                   radialaxis=dict(visible=True, range=[0, 1.1], gridcolor='#333')),
        legend=dict(orientation='h', y=-0.15)
    )
    _salvar(fig, '12_radar')


# ==============================================================================
# GRÁFICOS DE ANÁLISE ESTATÍSTICA
# ==============================================================================

def grafico_correlacao(corr_pearson, corr_spearman):
    """Heatmap dual de correlação."""
    print("📐 Gráfico de Correlação...")
    labels = ['Mortalidade', 'Cobertura', 'Positividade', 'Vacinal']
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Pearson', 'Spearman'], horizontal_spacing=0.15)
    fig.add_trace(go.Heatmap(z=corr_pearson.values, x=labels, y=labels,
                             colorscale='RdBu_r', zmin=-1, zmax=1, showscale=False,
                             text=corr_pearson.values.round(3), texttemplate='%{text}'), row=1, col=1)
    fig.add_trace(go.Heatmap(z=corr_spearman.values, x=labels, y=labels,
                             colorscale='RdBu_r', zmin=-1, zmax=1,
                             text=corr_spearman.values.round(3), texttemplate='%{text}',
                             colorbar=dict(title='ρ')), row=1, col=2)
    _layout_base(fig, '📐 Correlação: Pearson vs Spearman', 450)
    _salvar(fig, '13_correlacao')


def grafico_regressao(df_agg, resultado_reg):
    """Regressão + resíduos."""
    print("📉 Gráfico de Regressão...")
    fig = make_subplots(rows=1, cols=2, subplot_titles=['Regressão', 'Resíduos'])
    fig.add_trace(go.Scatter(x=df_agg['media_cobertura'], y=df_agg['media_mortalidade'],
                             mode='markers', marker=dict(color=CORES['secundaria'], size=8),
                             name='UFs', hovertext=df_agg['uf_nome']), row=1, col=1)
    x_r = np.linspace(df_agg['media_cobertura'].min(), df_agg['media_cobertura'].max(), 100)
    fig.add_trace(go.Scatter(x=x_r, y=resultado_reg['model'].predict(x_r.reshape(-1,1)),
                             mode='lines', line=dict(color=CORES['primaria'], dash='dash'),
                             name=f'R²={resultado_reg["r2"]:.3f}'), row=1, col=1)
    fig.add_trace(go.Scatter(x=resultado_reg['y_pred'], y=resultado_reg['residuos'],
                             mode='markers', marker=dict(color=CORES['alerta'], size=7),
                             name='Resíduos'), row=1, col=2)
    fig.add_hline(y=0, line_dash='dash', line_color='white', row=1, col=2)
    _layout_base(fig, '📉 Regressão Linear + Resíduos', 450)
    _salvar(fig, '14_regressao')


def grafico_pca_3d(df_pca, variance, df_master):
    """PCA 3D interativo."""
    print("🧬 Gráfico PCA 3D...")
    sigla_reg = df_master.drop_duplicates('uf_nome')[['uf_nome', 'regiao']]
    df_p = df_pca.merge(sigla_reg, on='uf_nome', how='left')

    fig = px.scatter_3d(df_p, x='PC1', y='PC2', z='PC3', color='regiao',
                        hover_name='uf_nome', color_discrete_map=PALETA_REGIOES,
                        title='🧬 PCA 3D — Perfil dos Estados',
                        labels={'PC1': f'PC1 ({variance[0]:.0%})',
                                'PC2': f'PC2 ({variance[1]:.0%})',
                                'PC3': f'PC3 ({variance[2]:.0%})'})
    _layout_base(fig, fig.layout.title.text, 600)
    fig.update_layout(scene=dict(bgcolor=CORES['plot_bg']))
    _salvar(fig, '15_pca_3d')


def grafico_kmeans(df_agg, resultado_km):
    """Elbow + Scatter de clusters."""
    print("🎯 Gráfico K-Means...")
    # Elbow
    fig_e = make_subplots(rows=1, cols=2, subplot_titles=['Elbow (Inércia)', 'Silhouette'])
    fig_e.add_trace(go.Scatter(x=resultado_km['k_range'], y=resultado_km['inertias'],
                               mode='lines+markers', line=dict(color=CORES['secundaria'])), row=1, col=1)
    fig_e.add_trace(go.Scatter(x=resultado_km['k_range'], y=resultado_km['silhouettes'],
                               mode='lines+markers', line=dict(color=CORES['terciaria'])), row=1, col=2)
    _layout_base(fig_e, '🎯 Elbow Method + Silhouette Score', 350)
    fig_e.update_layout(showlegend=False)
    _salvar(fig_e, '16_kmeans_elbow')

    # Clusters
    df_km = resultado_km['df_agg']
    fig_c = px.scatter(df_km, x='media_cobertura', y='media_mortalidade',
                       color=df_km['cluster'].astype(str), hover_name='uf_nome',
                       size='total_obitos', size_max=30,
                       color_discrete_sequence=[CORES['primaria'], CORES['terciaria'], CORES['secundaria']],
                       title='🎯 Clusters K-Means — Perfis de UFs')
    _layout_base(fig_c, fig_c.layout.title.text, 550)
    _salvar(fig_c, '17_kmeans_clusters')


def grafico_kpi_dashboard(df: pd.DataFrame):
    """Dashboard KPI com indicadores."""
    print("📊 Dashboard KPI...")
    ult = df['ano'].max()
    ant = ult - 1
    du, da = df[df['ano'] == ult], df[df['ano'] == ant]

    mort_u = (du['obitos'].sum() / du['populacao'].sum()) * 100000
    mort_a = (da['obitos'].sum() / da['populacao'].sum()) * 100000
    cob_u = (du['exames_realizados'].sum() / du['populacao'].sum()) * 100
    cob_a = (da['exames_realizados'].sum() / da['populacao'].sum()) * 100

    fig = make_subplots(rows=1, cols=4, specs=[[{'type':'indicator'}]*4],
                        subplot_titles=['Mortalidade/100k', 'Óbitos', 'Exames', 'Cobertura'])
    fig.add_trace(go.Indicator(mode='number+delta', value=round(mort_u, 2),
                               delta=dict(reference=round(mort_a, 2), relative=True),
                               number=dict(font=dict(color=CORES['primaria'], size=36))), row=1, col=1)
    fig.add_trace(go.Indicator(mode='number', value=du['obitos'].sum(),
                               number=dict(font=dict(color=CORES['alerta'], size=36), valueformat=',')), row=1, col=2)
    fig.add_trace(go.Indicator(mode='number', value=du['exames_realizados'].sum(),
                               number=dict(font=dict(color=CORES['terciaria'], size=36), valueformat=',')), row=1, col=3)
    fig.add_trace(go.Indicator(mode='number+delta', value=round(cob_u, 2),
                               delta=dict(reference=round(cob_a, 2), relative=True),
                               number=dict(font=dict(color=CORES['secundaria'], size=36), suffix='%')), row=1, col=4)
    _layout_base(fig, f'📊 Indicadores-Chave — {ult}', 250)
    _salvar(fig, '18_kpi_dashboard')


# ==============================================================================
# Função principal
# ==============================================================================

def gerar_todas_visualizacoes(df_master: pd.DataFrame, resultados_analise: dict):
    """Gera todos os 18 gráficos interativos."""
    print("\n" + "=" * 60)
    print("📊 GERANDO VISUALIZAÇÕES INTERATIVAS")
    print("=" * 60)

    # EDA (12 gráficos)
    grafico_mapa_coropletico(df_master)
    grafico_serie_temporal(df_master)
    grafico_bar_race(df_master)
    grafico_scatter_cobertura(df_master)
    grafico_heatmap_temporal(df_master)
    grafico_sunburst(df_master)
    grafico_treemap(df_master)
    grafico_boxplot_regional(df_master)
    grafico_painel_multi(df_master)
    grafico_funil(df_master)
    grafico_small_multiples(df_master)
    grafico_radar(df_master)

    # Análise estatística (5 gráficos)
    r = resultados_analise
    grafico_correlacao(r['correlacoes']['pearson'], r['correlacoes']['spearman'])
    grafico_regressao(r['kmeans']['df_agg'], r['regressao'])
    grafico_pca_3d(r['pca']['coords'], r['pca']['variance'], df_master)
    grafico_kmeans(r['kmeans']['df_agg'], r['kmeans'])
    grafico_kpi_dashboard(df_master)

    print("\n" + "=" * 60)
    n = len([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.html')])
    print(f"✅ {n} gráficos gerados em: {OUTPUT_DIR}/")
    print("=" * 60)
