#!/usr/bin/env python3
"""
Dashboard Interativo — Câncer do Colo do Útero no Brasil
=========================================================
Storytelling visual com filtros por ano, estado, região e métricas.

Uso:
  source .venv/bin/activate
  python dashboard.py

Acesse: http://localhost:8050
"""
import os
import json

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dash import Dash, dcc, html, Input, Output, callback

from src.config import DATA_DIR, CORES, PALETA_REGIOES, SIGLAS


# ==============================================================================
# Carregar Dados
# ==============================================================================
df_master = pd.read_csv(os.path.join(DATA_DIR, 'df_master.csv'))

GEOJSON_PATH = os.path.join(DATA_DIR, 'brazil_states.json')
with open(GEOJSON_PATH) as f:
    geojson_br = json.load(f)
for feat in geojson_br['features']:
    feat['id'] = feat['properties'].get('sigla', '')

ANOS = sorted([int(a) for a in df_master['ano'].unique()])
REGIOES = sorted(df_master['regiao'].unique().tolist())
ESTADOS = sorted(df_master['uf_nome'].unique().tolist())


# ==============================================================================
# App Dash
# ==============================================================================
app = Dash(__name__)
app.title = "🔬 Dashboard — Câncer do Colo do Útero"

# CSS inline para tema dark premium
DARK_BG = CORES['fundo']
CARD_BG = '#16213E'
TEXT_COLOR = CORES['texto']

card_style = {
    'backgroundColor': CARD_BG, 'borderRadius': '12px', 'padding': '20px',
    'marginBottom': '15px', 'boxShadow': '0 4px 20px rgba(0,0,0,0.4)',
    'border': '1px solid rgba(255,255,255,0.05)',
}
kpi_card_style = {
    **card_style,
    'textAlign': 'center', 'flex': '1', 'minWidth': '200px', 'margin': '0 8px',
}
filter_style = {
    'backgroundColor': '#0F3460', 'color': TEXT_COLOR, 'border': 'none',
    'borderRadius': '8px', 'padding': '5px',
}


# ==============================================================================
# Layout
# ==============================================================================
app.layout = html.Div(style={
    'backgroundColor': DARK_BG, 'color': TEXT_COLOR, 'minHeight': '100vh',
    'fontFamily': "'Inter', 'Segoe UI', sans-serif", 'padding': '0',
}, children=[

    # ─── Header ───
    html.Div(style={
        'background': 'linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%)',
        'padding': '30px 40px', 'borderBottom': '2px solid rgba(230,57,70,0.4)',
    }, children=[
        html.H1("🔬 Câncer do Colo do Útero no Brasil", style={
            'margin': '0 0 5px 0', 'fontSize': '28px', 'fontWeight': '700',
            'background': 'linear-gradient(90deg, #E63946, #F4A261)',
            'WebkitBackgroundClip': 'text', 'WebkitTextFillColor': 'transparent',
        }),
        html.P("Dashboard Interativo — Análise de Mortalidade, Rastreamento e Prevenção (2013–2024)",
               style={'margin': '0', 'color': '#888', 'fontSize': '14px'}),
    ]),

    # ─── Filtros ───
    html.Div(style={
        'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px',
        'padding': '20px 40px', 'alignItems': 'flex-end',
        'backgroundColor': 'rgba(15,52,96,0.3)',
    }, children=[
        html.Div(style={'flex': '1', 'minWidth': '180px'}, children=[
            html.Label("📅 Período", style={'fontWeight': '600', 'fontSize': '13px', 'marginBottom': '5px'}),
            dcc.RangeSlider(
                id='slider-anos', min=min(ANOS), max=max(ANOS),
                value=[min(ANOS), max(ANOS)], step=1,
                marks={a: {'label': str(a), 'style': {'color': '#888', 'fontSize': '11px'}} for a in ANOS},
                tooltip={'placement': 'bottom', 'always_visible': False},
            ),
        ]),
        html.Div(style={'flex': '0.5', 'minWidth': '200px'}, children=[
            html.Label("🗺️ Região", style={'fontWeight': '600', 'fontSize': '13px'}),
            dcc.Dropdown(
                id='dropdown-regiao', options=[{'label': r, 'value': r} for r in REGIOES],
                value=REGIOES, multi=True, placeholder='Todas',
                style={'backgroundColor': '#0F3460', 'color': '#222'},
            ),
        ]),
        html.Div(style={'flex': '0.5', 'minWidth': '200px'}, children=[
            html.Label("📍 Estado", style={'fontWeight': '600', 'fontSize': '13px'}),
            dcc.Dropdown(
                id='dropdown-estado', options=[{'label': e, 'value': e} for e in ESTADOS],
                value=[], multi=True, placeholder='Todos',
                style={'backgroundColor': '#0F3460', 'color': '#222'},
            ),
        ]),
        html.Div(style={'flex': '0.3', 'minWidth': '180px'}, children=[
            html.Label("📊 Métrica", style={'fontWeight': '600', 'fontSize': '13px'}),
            dcc.Dropdown(
                id='dropdown-metrica',
                options=[
                    {'label': '💀 Mortalidade/100k', 'value': 'taxa_mortalidade'},
                    {'label': '🔬 Cobertura Exames (%)', 'value': 'razao_exames_pop'},
                    {'label': '🧪 Positividade (%)', 'value': 'taxa_positividade'},
                    {'label': '💉 Cobertura Vacinal/100k', 'value': 'cobertura_vacinal_100k'},
                ],
                value='taxa_mortalidade',
                style={'backgroundColor': '#0F3460', 'color': '#222'},
            ),
        ]),
    ]),

    # ─── KPI Cards ───
    html.Div(id='kpi-cards', style={
        'display': 'flex', 'flexWrap': 'wrap', 'padding': '15px 40px', 'gap': '0',
    }),

    # ─── Storytelling Banner ───
    html.Div(id='story-banner', style={
        'padding': '15px 40px', 'margin': '0 40px 15px',
        'backgroundColor': 'rgba(230,57,70,0.1)', 'borderRadius': '10px',
        'borderLeft': '4px solid #E63946', 'fontSize': '14px', 'lineHeight': '1.6',
    }),

    # ─── Gráficos: Linha 1 (Mapa + Série Temporal) ───
    html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'padding': '0 40px', 'gap': '15px'}, children=[
        html.Div(style={**card_style, 'flex': '1.2', 'minWidth': '500px'}, children=[
            dcc.Graph(id='grafico-mapa', config={'displayModeBar': False}),
        ]),
        html.Div(style={**card_style, 'flex': '1', 'minWidth': '400px'}, children=[
            dcc.Graph(id='grafico-serie', config={'displayModeBar': False}),
        ]),
    ]),

    # ─── Gráficos: Linha 2 (Ranking + Scatter) ───
    html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'padding': '0 40px', 'gap': '15px'}, children=[
        html.Div(style={**card_style, 'flex': '1', 'minWidth': '400px'}, children=[
            dcc.Graph(id='grafico-ranking', config={'displayModeBar': False}),
        ]),
        html.Div(style={**card_style, 'flex': '1', 'minWidth': '400px'}, children=[
            dcc.Graph(id='grafico-scatter', config={'displayModeBar': False}),
        ]),
    ]),

    # ─── Gráficos: Linha 3 (Regional + Funil) ───
    html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'padding': '0 40px', 'gap': '15px'}, children=[
        html.Div(style={**card_style, 'flex': '1.3', 'minWidth': '500px'}, children=[
            dcc.Graph(id='grafico-regional', config={'displayModeBar': False}),
        ]),
        html.Div(style={**card_style, 'flex': '0.7', 'minWidth': '350px'}, children=[
            dcc.Graph(id='grafico-funil', config={'displayModeBar': False}),
        ]),
    ]),

    # ─── Footer ───
    html.Div(style={
        'textAlign': 'center', 'padding': '25px', 'color': '#555',
        'borderTop': '1px solid rgba(255,255,255,0.05)', 'marginTop': '20px',
    }, children=[
        html.P("Dados: DATASUS (SIM, SISCAN, SI-PNI, IBGE) | Desenvolvido por Iago Almeida",
               style={'margin': '0', 'fontSize': '12px'}),
    ]),
])


# ==============================================================================
# Callbacks
# ==============================================================================

def filtrar_dados(anos, regioes, estados):
    """Aplica filtros ao df_master."""
    df = df_master[df_master['ano'].between(anos[0], anos[1])]
    if regioes:
        df = df[df['regiao'].isin(regioes)]
    if estados:
        df = df[df['uf_nome'].isin(estados)]
    return df


@callback(
    Output('kpi-cards', 'children'),
    Output('story-banner', 'children'),
    Output('grafico-mapa', 'figure'),
    Output('grafico-serie', 'figure'),
    Output('grafico-ranking', 'figure'),
    Output('grafico-scatter', 'figure'),
    Output('grafico-regional', 'figure'),
    Output('grafico-funil', 'figure'),
    Input('slider-anos', 'value'),
    Input('dropdown-regiao', 'value'),
    Input('dropdown-estado', 'value'),
    Input('dropdown-metrica', 'value'),
)
def atualizar_dashboard(anos, regioes, estados, metrica):
    df = filtrar_dados(anos, regioes, estados)

    if df.empty:
        empty = go.Figure().update_layout(
            paper_bgcolor=CARD_BG, plot_bgcolor=CARD_BG,
            font_color=TEXT_COLOR, annotations=[dict(text="Sem dados", showarrow=False)]
        )
        return [], "Sem dados para os filtros selecionados.", empty, empty, empty, empty, empty, empty

    # Labels da métrica
    metrica_labels = {
        'taxa_mortalidade': ('Mortalidade', '/100k', '💀'),
        'razao_exames_pop': ('Cobertura', '%', '🔬'),
        'taxa_positividade': ('Positividade', '%', '🧪'),
        'cobertura_vacinal_100k': ('Vacinal', '/100k', '💉'),
    }
    met_nome, met_unid, met_icon = metrica_labels[metrica]

    # ─── KPI Cards ───
    ult_ano = df['ano'].max()
    ant_ano = ult_ano - 1
    df_ult = df[df['ano'] == ult_ano]
    df_ant = df[df['ano'] == ant_ano]

    pop_ult = df_ult['populacao'].sum()
    obt_ult = df_ult['obitos'].sum()
    exm_ult = df_ult['exames_realizados'].sum()
    vac_ult = df_ult['doses_aplicadas'].sum()

    # Se não há dados de vacina no ano selecionado, pegar último com dados
    vac_label_ano = ult_ano
    if vac_ult == 0:
        df_vac = df[df['doses_aplicadas'] > 0]
        if not df_vac.empty:
            vac_label_ano = df_vac['ano'].max()
            vac_ult = df_vac[df_vac['ano'] == vac_label_ano]['doses_aplicadas'].sum()

    mort_ult = (obt_ult / pop_ult * 100000) if pop_ult > 0 else 0
    cob_ult = (exm_ult / pop_ult * 100) if pop_ult > 0 else 0

    obt_ant = df_ant['obitos'].sum()
    pop_ant = df_ant['populacao'].sum()
    mort_ant = (obt_ant / pop_ant * 100000) if pop_ant > 0 else 0
    exm_ant = df_ant['exames_realizados'].sum()
    cob_ant = (exm_ant / pop_ant * 100) if pop_ant > 0 else 0

    def delta_pct(atual, anterior):
        if anterior == 0:
            return ''
        d = ((atual - anterior) / anterior) * 100
        cor = '#E63946' if d > 0 else '#2A9D8F'
        seta = '▲' if d > 0 else '▼'
        return html.Span(f" {seta} {abs(d):.1f}%", style={'color': cor, 'fontSize': '13px'})

    vac_label = f'💉 HPV ({vac_label_ano})' if vac_label_ano != ult_ano else '💉 Doses HPV'

    kpis = [
        ('💀 Mortalidade', f'{mort_ult:,.2f}/100k', delta_pct(mort_ult, mort_ant), CORES['primaria']),
        ('⚰️ Óbitos', f'{obt_ult:,.0f}', delta_pct(obt_ult, obt_ant), CORES['alerta']),
        ('🔬 Exames', f'{exm_ult:,.0f}', delta_pct(exm_ult, exm_ant), CORES['terciaria']),
        ('📊 Cobertura', f'{cob_ult:,.2f}%', delta_pct(cob_ult, cob_ant), CORES['secundaria']),
        (vac_label, f'{vac_ult:,.0f}', '', '#A855F7'),
    ]

    kpi_children = []
    for titulo, valor, delta, cor in kpis:
        kpi_children.append(html.Div(style=kpi_card_style, children=[
            html.P(titulo, style={'margin': '0', 'fontSize': '12px', 'color': '#888'}),
            html.H2(valor, style={'margin': '5px 0', 'color': cor, 'fontSize': '24px', 'fontWeight': '700'}),
            html.P(delta, style={'margin': '0'}) if delta else html.P(),
        ]))

    # ─── Storytelling ───
    n_ufs = df['uf_nome'].nunique()
    total_obitos = df['obitos'].sum()
    total_exames = df['exames_realizados'].sum()
    uf_pior = df.groupby('uf_nome')['taxa_mortalidade'].mean().idxmax() if not df.empty else '—'
    uf_melhor = df.groupby('uf_nome')['taxa_mortalidade'].mean().idxmin() if not df.empty else '—'

    story = [
        html.Strong("📖 Insights do Período Selecionado: "),
        f"Entre {anos[0]} e {anos[1]}, foram registrados ",
        html.Strong(f"{total_obitos:,.0f} óbitos"),
        f" por câncer de colo do útero em {n_ufs} estados, com ",
        html.Strong(f"{total_exames:,.0f} exames"),
        f" de Papanicolau realizados. ",
        html.Strong(f"{uf_pior}"),
        " apresenta a maior taxa média de mortalidade, enquanto ",
        html.Strong(f"{uf_melhor}"),
        " tem a menor — evidenciando a ",
        html.Span("desigualdade regional", style={'color': '#E63946', 'fontWeight': '600'}),
        " no acesso ao rastreamento.",
    ]

    # ─── Mapa Coroplético ───
    df_mapa = df.groupby(['sigla_uf', 'uf_nome', 'regiao']).agg(
        val=(metrica, 'mean')
    ).reset_index()

    fig_mapa = px.choropleth(
        df_mapa, geojson=geojson_br, locations='sigla_uf', color='val',
        color_continuous_scale='YlOrRd', scope='south america',
        hover_name='uf_nome',
        hover_data={'val': ':.2f', 'sigla_uf': False},
        labels={'val': f'{met_nome} ({met_unid})'},
    )
    fig_mapa.update_geos(fitbounds="locations", visible=False, bgcolor='rgba(0,0,0,0)')
    fig_mapa.update_layout(
        title=f'{met_icon} {met_nome} Média por Estado ({anos[0]}-{anos[1]})',
        height=420, margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor=CARD_BG, font_color=TEXT_COLOR, title_font_size=14,
        coloraxis_colorbar=dict(thickness=15, len=0.6),
    )

    # ─── Série Temporal ───
    df_ts = df.groupby('ano').agg(ob=('obitos','sum'), pop=('populacao','sum'),
                                   ex=('exames_realizados','sum'), dg=('diagnosticos_positivos','sum'),
                                   vc=('doses_aplicadas','sum')).reset_index()
    df_ts['taxa_mortalidade'] = (df_ts['ob'] / df_ts['pop']) * 100000
    df_ts['razao_exames_pop'] = (df_ts['ex'] / df_ts['pop']) * 100
    df_ts['taxa_positividade'] = np.where(df_ts['ex'] > 0, (df_ts['dg'] / df_ts['ex']) * 100, 0)
    df_ts['cobertura_vacinal_100k'] = (df_ts['vc'] / df_ts['pop']) * 100000

    fig_serie = go.Figure()
    fig_serie.add_trace(go.Scatter(
        x=df_ts['ano'], y=df_ts[metrica], mode='lines+markers',
        line=dict(color=CORES['primaria'], width=3), marker=dict(size=8),
        name=met_nome, hovertemplate=f'<b>%{{x}}</b><br>{met_nome}: %{{y:.2f}}{met_unid}<extra></extra>'
    ))
    mm = df_ts[metrica].rolling(3, center=True).mean()
    fig_serie.add_trace(go.Scatter(
        x=df_ts['ano'], y=mm, mode='lines', name='Média Móvel (3a)',
        line=dict(color=CORES['secundaria'], width=2, dash='dash'),
    ))
    if anos[0] <= 2020 <= anos[1]:
        fig_serie.add_vrect(x0=2019.5, x1=2021.5, fillcolor=CORES['alerta'], opacity=0.12,
                            annotation_text="COVID-19", annotation_position="top left",
                            annotation_font_color=CORES['alerta'], annotation_font_size=10)
    fig_serie.update_layout(
        title=f'📈 Evolução de {met_nome}',
        height=420, paper_bgcolor=CARD_BG, plot_bgcolor='rgba(0,0,0,0)',
        font_color=TEXT_COLOR, title_font_size=14,
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Ano'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title=f'{met_nome} ({met_unid})'),
        hovermode='x unified', legend=dict(orientation='h', y=1.08),
        margin=dict(l=50, r=20, t=50, b=40),
    )

    # ─── Ranking Bar ───
    df_rank = df.groupby(['uf_nome', 'sigla_uf', 'regiao']).agg(
        val=(metrica, 'mean')
    ).reset_index().sort_values('val', ascending=True).tail(15)

    fig_rank = px.bar(
        df_rank, x='val', y='sigla_uf', color='regiao', orientation='h',
        color_discrete_map=PALETA_REGIOES,
        hover_name='uf_nome', hover_data={'val': ':.2f', 'sigla_uf': False},
        labels={'val': f'{met_nome} ({met_unid})', 'sigla_uf': ''},
    )
    fig_rank.update_layout(
        title=f'🏆 Top 15 — Maior {met_nome} (Média)',
        height=420, paper_bgcolor=CARD_BG, plot_bgcolor='rgba(0,0,0,0)',
        font_color=TEXT_COLOR, title_font_size=14,
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(categoryorder='total ascending'),
        legend=dict(orientation='h', y=1.08, title=''),
        margin=dict(l=50, r=20, t=50, b=40),
    )

    # ─── Scatter ───
    df_sc = df.groupby(['uf_nome', 'sigla_uf', 'regiao']).agg(
        cob=('razao_exames_pop','mean'), mort=('taxa_mortalidade','mean'),
        pop=('populacao','mean'), obt=('obitos','sum'),
    ).reset_index()

    fig_sc = px.scatter(
        df_sc, x='cob', y='mort', size='pop', color='regiao',
        hover_name='uf_nome', size_max=45,
        color_discrete_map=PALETA_REGIOES, trendline='ols',
        labels={'cob': 'Cobertura (%)', 'mort': 'Mortalidade/100k'},
    )
    for _, row in df_sc.iterrows():
        fig_sc.add_annotation(x=row['cob'], y=row['mort'], text=row['sigla_uf'],
                              showarrow=False, font=dict(size=8, color='#aaa'), yshift=10)
    fig_sc.update_layout(
        title='🔬 Cobertura vs Mortalidade',
        height=420, paper_bgcolor=CARD_BG, plot_bgcolor='rgba(0,0,0,0)',
        font_color=TEXT_COLOR, title_font_size=14,
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        legend=dict(orientation='h', y=1.08, title=''),
        margin=dict(l=50, r=20, t=50, b=40),
    )

    # ─── Regional (Multi-line) ───
    df_reg = df[df['regiao'] != 'Outros'].groupby(['ano', 'regiao']).agg(
        ob=('obitos','sum'), pop=('populacao','sum'), ex=('exames_realizados','sum'),
        dg=('diagnosticos_positivos','sum'), vc=('doses_aplicadas','sum'),
    ).reset_index()
    df_reg['taxa_mortalidade'] = (df_reg['ob'] / df_reg['pop']) * 100000
    df_reg['razao_exames_pop'] = (df_reg['ex'] / df_reg['pop']) * 100
    df_reg['taxa_positividade'] = np.where(df_reg['ex'] > 0, (df_reg['dg'] / df_reg['ex']) * 100, 0)
    df_reg['cobertura_vacinal_100k'] = (df_reg['vc'] / df_reg['pop']) * 100000

    fig_reg = px.line(
        df_reg, x='ano', y=metrica, color='regiao',
        color_discrete_map=PALETA_REGIOES, markers=True,
        labels={metrica: f'{met_nome} ({met_unid})', 'ano': 'Ano', 'regiao': 'Região'},
    )
    fig_reg.update_layout(
        title=f'📈 {met_nome} por Região',
        height=420, paper_bgcolor=CARD_BG, plot_bgcolor='rgba(0,0,0,0)',
        font_color=TEXT_COLOR, title_font_size=14,
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        legend=dict(orientation='h', y=1.08, title=''),
        margin=dict(l=50, r=20, t=50, b=40),
        hovermode='x unified',
    )

    # ─── Funil ───
    df_fun = df[df['ano'] == ult_ano]
    etapas = ['População Alvo', 'Examinadas (Papanicolau)', 'Diagnósticos Positivos', 'Óbitos']
    vals = [df_fun['populacao'].sum(), df_fun['exames_realizados'].sum(),
            df_fun['diagnosticos_positivos'].sum(), df_fun['obitos'].sum()]

    fig_fun = go.Figure(go.Funnel(
        y=etapas, x=vals, textinfo='value+percent initial', textposition='inside',
        marker=dict(color=[CORES['secundaria'], CORES['terciaria'], CORES['alerta'], CORES['primaria']]),
        connector=dict(line=dict(color='rgba(255,255,255,0.1)', width=1)),
    ))
    fig_fun.update_layout(
        title=f'🔻 Funil do Rastreamento ({ult_ano})',
        height=420, paper_bgcolor=CARD_BG, plot_bgcolor='rgba(0,0,0,0)',
        font_color=TEXT_COLOR, title_font_size=14,
        margin=dict(l=20, r=20, t=50, b=20),
    )

    return kpi_children, story, fig_mapa, fig_serie, fig_rank, fig_sc, fig_reg, fig_fun


# ==============================================================================
# Run
# ==============================================================================
if __name__ == '__main__':
    print("🚀 Dashboard iniciando em http://localhost:8050")
    app.run(debug=False, host='0.0.0.0', port=8050)
