"""
Módulo de análise estatística.
Correlações, ANOVA, Regressão, PCA e Clusterização.
"""
import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score


FEATURES = ['media_mortalidade', 'media_cobertura', 'media_positividade', 'media_cobertura_vacinal']


def analise_correlacoes(df_agg: pd.DataFrame) -> dict:
    """Calcula correlações Pearson, Spearman e Kendall."""
    print("\n📐 ANÁLISE DE CORRELAÇÃO")
    print("=" * 60)

    corr_pearson = df_agg[FEATURES].corr(method='pearson')
    corr_spearman = df_agg[FEATURES].corr(method='spearman')

    # Correlação-chave: Cobertura vs Mortalidade
    rho, p = stats.spearmanr(df_agg['media_cobertura'], df_agg['media_mortalidade'])
    print(f"  Cobertura vs Mortalidade (Spearman): ρ={rho:.4f}, p={p:.4f} "
          f"{'✅ Significativo' if p < 0.05 else '⚠️ Não significativo'}")

    rho2, p2 = stats.spearmanr(df_agg['total_exames'], df_agg['total_diagnosticos'])
    print(f"  Exames vs Diagnósticos (Spearman):   ρ={rho2:.4f}, p={p2:.4f}")

    return {
        'pearson': corr_pearson,
        'spearman': corr_spearman,
        'cob_vs_mort': {'rho': rho, 'p': p},
    }


def analise_anova(df_master: pd.DataFrame) -> dict:
    """Testa diferenças regionais com ANOVA e Kruskal-Wallis."""
    print("\n📊 ANOVA / KRUSKAL-WALLIS")
    print("=" * 60)

    regioes = [r for r in df_master['regiao'].unique() if r != 'Outros']
    grupos_mort = [df_master[df_master['regiao'] == r]['taxa_mortalidade'].values for r in regioes]
    grupos_cob = [df_master[df_master['regiao'] == r]['razao_exames_pop'].values for r in regioes]

    f_m, p_m = stats.f_oneway(*grupos_mort)
    h_m, pk_m = stats.kruskal(*grupos_mort)
    f_c, p_c = stats.f_oneway(*grupos_cob)
    h_c, pk_c = stats.kruskal(*grupos_cob)

    print(f"  Mortalidade - ANOVA: F={f_m:.3f}, p={p_m:.6f} | Kruskal: H={h_m:.3f}, p={pk_m:.6f}")
    print(f"  Cobertura   - ANOVA: F={f_c:.3f}, p={p_c:.6f} | Kruskal: H={h_c:.3f}, p={pk_c:.6f}")

    return {
        'mortalidade': {'F': f_m, 'p_anova': p_m, 'H': h_m, 'p_kruskal': pk_m},
        'cobertura': {'F': f_c, 'p_anova': p_c, 'H': h_c, 'p_kruskal': pk_c},
    }


def analise_regressao(df_agg: pd.DataFrame) -> dict:
    """Regressão linear simples: Cobertura → Mortalidade."""
    print("\n📉 REGRESSÃO LINEAR")
    print("=" * 60)

    X = df_agg[['media_cobertura']].values
    y = df_agg['media_mortalidade'].values

    model = LinearRegression().fit(X, y)
    y_pred = model.predict(X)
    residuos = y - y_pred

    print(f"  Coeficiente (β₁): {model.coef_[0]:.4f}")
    print(f"  Intercepto (β₀):  {model.intercept_:.4f}")
    print(f"  R²:               {model.score(X, y):.4f}")

    return {
        'model': model,
        'y_pred': y_pred,
        'residuos': residuos,
        'r2': model.score(X, y),
        'coef': model.coef_[0],
        'intercept': model.intercept_,
    }


def analise_pca(df_agg: pd.DataFrame) -> dict:
    """PCA com 3 componentes para visualização 3D."""
    print("\n🧬 PCA (3 COMPONENTES)")
    print("=" * 60)

    X = StandardScaler().fit_transform(df_agg[FEATURES])
    pca = PCA(n_components=3)
    coords = pca.fit_transform(X)

    df_pca = pd.DataFrame(coords, columns=['PC1', 'PC2', 'PC3'])
    df_pca['uf_nome'] = df_agg['uf_nome'].values

    var = pca.explained_variance_ratio_
    print(f"  PC1: {var[0]:.1%} | PC2: {var[1]:.1%} | PC3: {var[2]:.1%} | Total: {sum(var):.1%}")

    return {'coords': df_pca, 'variance': var, 'pca_model': pca}


def analise_kmeans(df_agg: pd.DataFrame, k: int = 3) -> dict:
    """K-Means com Elbow Method e Silhouette Score."""
    print("\n🎯 K-MEANS CLUSTERING")
    print("=" * 60)

    X = StandardScaler().fit_transform(df_agg[FEATURES])

    # Elbow + Silhouette
    inertias, silhouettes = [], []
    for ki in range(2, 8):
        km = KMeans(n_clusters=ki, random_state=42, n_init=10)
        labels = km.fit_predict(X)
        inertias.append(km.inertia_)
        silhouettes.append(silhouette_score(X, labels))

    # Fit final
    km_final = KMeans(n_clusters=k, random_state=42, n_init=10)
    df_agg = df_agg.copy()
    df_agg['cluster'] = km_final.fit_predict(X)

    print(f"  k={k} | Silhouette: {silhouettes[k - 2]:.3f}")
    print(f"\n  Perfil dos clusters:")
    print(df_agg.groupby('cluster')[FEATURES].mean().round(2).to_string())

    return {
        'df_agg': df_agg,
        'inertias': inertias,
        'silhouettes': silhouettes,
        'k_range': list(range(2, 8)),
    }


def executar_todas_analises(df_master: pd.DataFrame, df_agg: pd.DataFrame) -> dict:
    """Executa todas as análises estatísticas."""
    print("\n" + "=" * 60)
    print("🔬 ANÁLISE ESTATÍSTICA AVANÇADA")
    print("=" * 60)

    return {
        'correlacoes': analise_correlacoes(df_agg),
        'anova': analise_anova(df_master),
        'regressao': analise_regressao(df_agg),
        'pca': analise_pca(df_agg),
        'kmeans': analise_kmeans(df_agg),
    }
