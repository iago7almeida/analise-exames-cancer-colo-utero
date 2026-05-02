"""
Módulo de Data Wrangling.
Limpeza, transformação wide→long, merge e engenharia de atributos.
"""
import os

import numpy as np
import pandas as pd

from src.config import DATA_DIR, SIGLAS, REGIOES


def _classificar_regiao(uf: str) -> str:
    """Retorna a região brasileira do estado."""
    for regiao, estados in REGIOES.items():
        if uf in estados:
            return regiao
    return 'Outros'


def transformar_para_long(df: pd.DataFrame, nome_valor: str,
                          colunas_fixas=('id_uf', 'uf_nome')) -> pd.DataFrame:
    """Transforma DataFrame wide (anos em colunas) para formato long."""
    colunas_fixas = list(colunas_fixas)

    if 'id_uf' in df.columns:
        df = df[pd.to_numeric(df['id_uf'], errors='coerce').notnull()].copy()

    colunas_anos = [c for c in df.columns
                    if c not in colunas_fixas and str(c).strip().isdigit()]

    df_long = pd.melt(
        df, id_vars=colunas_fixas, value_vars=colunas_anos,
        var_name='ano', value_name=nome_valor
    )

    df_long['ano'] = pd.to_numeric(df_long['ano'], errors='coerce')
    df_long = df_long.dropna(subset=['ano'])
    df_long['ano'] = df_long['ano'].astype(int)

    # Limpeza de formatos numéricos brasileiros (ex: "1.000.000" → 1000000)
    # Usa pd.api.types para detectar strings corretamente (cobre object e StringDtype)
    if pd.api.types.is_string_dtype(df_long[nome_valor]):
        df_long[nome_valor] = (df_long[nome_valor].astype(str)
                               .str.replace('.', '', regex=False)
                               .str.replace(',', '.', regex=False)
                               .str.strip())

    df_long[nome_valor] = pd.to_numeric(df_long[nome_valor], errors='coerce').fillna(0)
    return df_long


def construir_master(dados: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Constrói o DataFrame master a partir dos 5 datasets extraídos.
    Inclui feature engineering e classificação regional.
    """
    cache_path = os.path.join(DATA_DIR, 'df_master.csv')
    if os.path.exists(cache_path):
        print("📂 Carregando df_master do cache...")
        return pd.read_csv(cache_path)

    print("🔧 Construindo df_master...")

    # 1. Transformar para formato long
    df_pop = transformar_para_long(dados['populacao'], 'populacao')
    df_obt = transformar_para_long(dados['obitos'], 'obitos')
    df_exm = transformar_para_long(dados['exames'], 'exames_realizados')
    df_diag = transformar_para_long(dados['diagnosticos'], 'diagnosticos_positivos')
    df_imun = transformar_para_long(dados['imunizacoes'], 'doses_aplicadas')

    # Normalizar id_uf para int-string em todos (corrige '11.0' → '11')
    for d in [df_pop, df_obt, df_exm, df_diag, df_imun]:
        d['id_uf'] = pd.to_numeric(d['id_uf'], errors='coerce')
        d.dropna(subset=['id_uf'], inplace=True)
        d['id_uf'] = d['id_uf'].astype(int).astype(str)

    # 2. Merge progressivo
    df = df_pop.merge(df_obt, on=['id_uf', 'uf_nome', 'ano'], how='left')
    df = df.merge(df_exm, on=['id_uf', 'uf_nome', 'ano'], how='left')
    df = df.merge(df_diag, on=['id_uf', 'uf_nome', 'ano'], how='left')
    df = df.merge(df_imun, on=['id_uf', 'uf_nome', 'ano'], how='left')
    df = df.fillna(0)

    # Limpar linhas sem UF válida
    df = df[pd.to_numeric(df['id_uf'], errors='coerce').notnull()]
    df['id_uf'] = df['id_uf'].astype(int)

    # 3. Feature Engineering — KPIs
    df['taxa_mortalidade'] = np.where(
        df['populacao'] > 0,
        (df['obitos'] / df['populacao']) * 100000, 0
    )
    df['razao_exames_pop'] = np.where(
        df['populacao'] > 0,
        (df['exames_realizados'] / df['populacao']) * 100, 0
    )
    df['taxa_positividade'] = np.where(
        df['exames_realizados'] > 0,
        (df['diagnosticos_positivos'] / df['exames_realizados']) * 100, 0
    )
    df['cobertura_vacinal_100k'] = np.where(
        df['populacao'] > 0,
        (df['doses_aplicadas'] / df['populacao']) * 100000, 0
    )

    # 4. Região, sigla, código geo
    df['regiao'] = df['uf_nome'].apply(_classificar_regiao)
    df['sigla_uf'] = df['uf_nome'].map(SIGLAS)
    df['cod_uf_geo'] = df['id_uf'].astype(str).str.zfill(2)

    # 5. Salvar cache
    df.to_csv(cache_path, index=False)
    print(f"💾 df_master salvo: {cache_path}")

    return df


def agregar_por_uf(df_master: pd.DataFrame, ano_max: int = 2022) -> pd.DataFrame:
    """Agrega dados por UF para análises de correlação e clustering."""
    df = df_master[df_master['ano'] <= ano_max].copy()

    return df.groupby('uf_nome').agg(
        media_mortalidade=('taxa_mortalidade', 'mean'),
        media_cobertura=('razao_exames_pop', 'mean'),
        media_positividade=('taxa_positividade', 'mean'),
        media_cobertura_vacinal=('cobertura_vacinal_100k', 'mean'),
        total_obitos=('obitos', 'sum'),
        total_diagnosticos=('diagnosticos_positivos', 'sum'),
        total_doses_hpv=('doses_aplicadas', 'sum'),
        total_exames=('exames_realizados', 'sum'),
    ).reset_index()
