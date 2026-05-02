#!/usr/bin/env python3
"""
Análise de Dados: Prevenção e Mortalidade do Câncer de Colo do Útero no Brasil
===============================================================================

Pipeline completo:
  1. Extração de dados do DATASUS (com cache CSV)
  2. Data Wrangling e Feature Engineering
  3. Análise Estatística Avançada
  4. Geração de 18 Visualizações Interativas (Plotly → HTML)

Uso:
  source .venv/bin/activate
  python main.py
"""
import time
import plotly.io as pio

from src.config import PLOTLY_TEMPLATE, OUTPUT_DIR
from src.extraction import extrair_todos
from src.wrangling import construir_master, agregar_por_uf
from src.analysis import executar_todas_analises
from src.visualization import gerar_todas_visualizacoes


def main():
    inicio = time.time()

    print("🔬 ANÁLISE DE DADOS — CÂNCER DO COLO DO ÚTERO")
    print("=" * 60)

    # Configurar tema Plotly
    pio.templates.default = PLOTLY_TEMPLATE

    # 1. Extração
    dados = extrair_todos()

    # 2. Wrangling
    print("\n🔧 DATA WRANGLING")
    print("=" * 60)
    df_master = construir_master(dados)
    df_agg = agregar_por_uf(df_master)

    print(f"\n📋 df_master: {df_master.shape[0]} linhas × {df_master.shape[1]} colunas")
    print(f"📋 Período: {df_master['ano'].min()} – {df_master['ano'].max()}")
    print(f"📋 Estados: {df_master['uf_nome'].nunique()}")

    # 3. Análise Estatística
    resultados = executar_todas_analises(df_master, df_agg)

    # 4. Visualizações
    gerar_todas_visualizacoes(df_master, resultados)

    elapsed = time.time() - inicio
    print(f"\n⏱️  Tempo total: {elapsed:.1f}s")
    print(f"\n🎉 Abra os gráficos em: {OUTPUT_DIR}/")
    print("   Cada arquivo .html é um gráfico interativo — abra no navegador!")


if __name__ == '__main__':
    main()
