"""
Módulo de extração de dados do DATASUS (TabNet).
Web scraping automatizado com cache local em CSV.
"""
import os
import re
import ast
import io
import time

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.config import (
    DATA_DIR, HEADERS_TABNET,
    PAYLOAD_POPULACAO, PAYLOAD_OBITOS, PAYLOAD_IMUNIZACOES,
    PAYLOAD_DIAGNOSTICOS, PAYLOAD_EXAMES_BASE, PAYLOAD_EXAMES_FILTROS,
)


# ==============================================================================
# Funções genéricas de extração
# ==============================================================================

def _carregar_cache(nome: str) -> pd.DataFrame | None:
    """Retorna DataFrame do cache CSV se existir, senão None."""
    caminho = os.path.join(DATA_DIR, f'{nome}.csv')
    if os.path.exists(caminho):
        print(f"  📂 Cache encontrado: {caminho}")
        return pd.read_csv(caminho)
    return None


def _salvar_cache(df: pd.DataFrame, nome: str):
    """Salva DataFrame como CSV no diretório de cache."""
    caminho = os.path.join(DATA_DIR, f'{nome}.csv')
    df.to_csv(caminho, index=False)
    print(f"  💾 Salvo em: {caminho}")


def _extrair_tabnet_html(url: str, payload: str) -> pd.DataFrame:
    """Extrai tabela HTML do TabNet (SIM, IBGE)."""
    headers = {**HEADERS_TABNET, 'Referer': url}
    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()
    response.encoding = 'ISO-8859-1'

    df = pd.read_html(io.StringIO(response.text))[0]
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(0)

    df = df.rename(columns={df.columns[0]: 'Unidade da Federação'})
    colunas = [c for c in df.columns if c == 'Unidade da Federação' or str(c).isdigit()]
    df = df[colunas]

    if str(df.iloc[0, 0]).upper() == 'TOTAL':
        df = df.iloc[1:].reset_index(drop=True)

    split = df['Unidade da Federação'].str.split(' ', n=1, expand=True)
    df['id_uf'] = split[0]
    df['uf_nome'] = split[1]
    df = df.drop(columns=['Unidade da Federação'])

    cols = ['id_uf', 'uf_nome'] + [c for c in df.columns if c not in ['id_uf', 'uf_nome']]
    return df[cols]


def _extrair_tabnet_js(url: str, payload: str) -> pd.DataFrame:
    """Extrai dados de resposta JavaScript do TabNet (SISCAN, PNI)."""
    headers = {**HEADERS_TABNET, 'Referer': url}
    response = requests.post(url, data=payload, headers=headers)
    html = response.text

    match = re.search(r"data\.addRows\(\[(.*?)\]\);", html, re.DOTALL)
    colunas = re.findall(r"data\.addColumn\('.*?',\s*'(.*?)'\);", html)

    if not match or not colunas:
        return pd.DataFrame()

    dados_js = match.group(1)
    dados_limpos = re.sub(r"\{v:\s*([^,]+),.*?\}", r"\1", dados_js)
    lista = ast.literal_eval(f"[{dados_limpos}]")
    df = pd.DataFrame(lista, columns=colunas)

    # Limpar e formatar
    first_col = df.columns[0]
    df = df[df[first_col] != 'Total'].copy()
    split = df[first_col].str.split(' ', n=1, expand=True)
    df['id_uf'] = split[0]
    df['uf_nome'] = split[1]
    df = df.drop(columns=[first_col])
    cols = ['id_uf', 'uf_nome'] + [c for c in df.columns if c not in ['id_uf', 'uf_nome']]
    return df[cols]


# ==============================================================================
# Funções específicas de extração por dataset
# ==============================================================================

def extrair_populacao() -> pd.DataFrame:
    """Extrai população feminina residente por UF (IBGE)."""
    print("📊 [1/5] População Feminina...")
    cache = _carregar_cache('populacao_feminina')
    if cache is not None:
        return cache

    df = _extrair_tabnet_html(PAYLOAD_POPULACAO['url'], PAYLOAD_POPULACAO['data'])
    _salvar_cache(df, 'populacao_feminina')
    return df


def extrair_obitos() -> pd.DataFrame:
    """Extrai óbitos por neoplasia maligna do colo do útero - CID-10 C53 (SIM)."""
    print("📊 [2/5] Óbitos (CID-10 C53)...")
    cache = _carregar_cache('obitos_neop_utero')
    if cache is not None:
        return cache

    df = _extrair_tabnet_html(PAYLOAD_OBITOS['url'], PAYLOAD_OBITOS['data'])
    _salvar_cache(df, 'obitos_neop_utero')
    return df


def extrair_exames_cito() -> pd.DataFrame:
    """Extrai exames citopatológicos do SISCAN (ano a ano)."""
    print("📊 [3/5] Exames Citopatológicos (SISCAN)...")
    cache = _carregar_cache('exames_cito')
    if cache is not None:
        return cache

    url = "http://tabnet.datasus.gov.br/cgi/webtabx.exe?SISCAN/cito_colo_pacbr.def"
    headers = {
        **HEADERS_TABNET,
        'Referer': 'http://tabnet.datasus.gov.br/cgi/dhdat.exe?SISCAN/cito_colo_pacbr.def',
        'cache-control': 'max-age=0',
    }

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=2, status_forcelist=[500, 502, 503, 504],
                    allowed_methods=["POST"])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.headers.update(headers)

    lista_dfs = []
    for ano in range(2013, 2025):
        print(f"    Baixando {ano}...", end=" ")
        parte_ano = f"&PAno+competencia={ano}%7C{ano}%7C4"
        payload = PAYLOAD_EXAMES_BASE + parte_ano + PAYLOAD_EXAMES_FILTROS

        try:
            resp = session.post(url, data=payload, timeout=180)
            resp.raise_for_status()
            html = resp.text

            match = re.search(r"data\.addRows\(\[(.*?)\]\);", html, re.DOTALL)
            cols = re.findall(r"data\.addColumn\('.*?',\s*'(.*?)'\);", html)

            if match and cols:
                dados = re.sub(r"\{v:\s*([^,]+),.*?\}", r"\1", match.group(1))
                df_t = pd.DataFrame(ast.literal_eval(f"[{dados}]"), columns=cols)
                if 'Total' in df_t.iloc[:, 0].values:
                    df_t = df_t[df_t.iloc[:, 0] != 'Total']
                df_t.set_index(df_t.columns[0], inplace=True)
                df_t.rename(columns={df_t.columns[0]: str(ano)}, inplace=True)
                df_t = df_t[[str(ano)]]
                lista_dfs.append(df_t)
                print("✅")
            else:
                print("⚠️ Sem dados")
        except Exception as e:
            print(f"❌ {e}")

        time.sleep(2)

    if not lista_dfs:
        return pd.DataFrame()

    df = pd.concat(lista_dfs, axis=1).reset_index()
    df.fillna(0, inplace=True)
    split = df.iloc[:, 0].str.split(' ', n=1, expand=True)
    df['id_uf'] = split[0]
    df['uf_nome'] = split[1]
    df.drop(columns=[df.columns[0]], inplace=True)
    cols = ['id_uf', 'uf_nome'] + [c for c in df.columns if c not in ['id_uf', 'uf_nome']]
    df = df[cols].sort_values('id_uf')

    _salvar_cache(df, 'exames_cito')
    return df


def extrair_imunizacoes() -> pd.DataFrame:
    """Extrai doses de vacina HPV aplicadas (SI-PNI)."""
    print("📊 [4/5] Imunizações HPV...")
    cache = _carregar_cache('imunizacoes_hpv')
    if cache is not None:
        return cache

    df = _extrair_tabnet_js(PAYLOAD_IMUNIZACOES['url'], PAYLOAD_IMUNIZACOES['data'])
    _salvar_cache(df, 'imunizacoes_hpv')
    return df


def extrair_diagnosticos() -> pd.DataFrame:
    """Extrai diagnósticos histopatológicos (SISCAN)."""
    print("📊 [5/5] Diagnósticos Histopatológicos...")
    cache = _carregar_cache('diagnosticos_histo')
    if cache is not None:
        return cache

    df = _extrair_tabnet_js(PAYLOAD_DIAGNOSTICOS['url'], PAYLOAD_DIAGNOSTICOS['data'])
    _salvar_cache(df, 'diagnosticos_histo')
    return df


def extrair_todos() -> dict[str, pd.DataFrame]:
    """Executa todas as extrações e retorna dict com os DataFrames."""
    print("=" * 60)
    print("🚀 INICIANDO EXTRAÇÃO DE DADOS DO DATASUS")
    print("=" * 60)

    dados = {
        'populacao': extrair_populacao(),
        'obitos': extrair_obitos(),
        'exames': extrair_exames_cito(),
        'imunizacoes': extrair_imunizacoes(),
        'diagnosticos': extrair_diagnosticos(),
    }

    print("=" * 60)
    print("✅ EXTRAÇÃO CONCLUÍDA!")
    for nome, df in dados.items():
        print(f"   {nome}: {df.shape}")
    print("=" * 60)

    return dados
