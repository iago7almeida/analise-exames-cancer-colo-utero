# 🔬 Análise de Dados — Câncer do Colo do Útero no Brasil

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?logo=plotly&logoColor=white)
![Dash](https://img.shields.io/badge/Dash-2.14+-00B4D8?logo=plotly&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3+-F7931E?logo=scikitlearn&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

> Pipeline de Data Science completo para análise de mortalidade, rastreamento (Papanicolau) e vacinação HPV, com dados extraídos automaticamente do DATASUS.

---

## 📌 Objetivo

Investigar a efetividade das políticas públicas de prevenção ao câncer de colo do útero no Brasil, respondendo à pergunta:

> *A cobertura de rastreamento e vacinação HPV está associada a menores taxas de mortalidade nos estados brasileiros?*

---

## 🗂️ Estrutura do Projeto

```
├── main.py                    # Pipeline principal (extração → análise → gráficos)
├── dashboard.py               # Dashboard interativo Dash (http://localhost:8050)
├── src/
│   ├── __init__.py
│   ├── config.py              # Constantes, paletas, payloads do DATASUS
│   ├── extraction.py          # Web scraping TabNet com cache CSV
│   ├── wrangling.py           # Limpeza, merge, feature engineering
│   ├── analysis.py            # Correlação, ANOVA, Regressão, PCA, K-Means
│   └── visualization.py       # 18 gráficos Plotly interativos
├── data/                      # Cache CSV (gerado automaticamente)
├── output/                    # Gráficos HTML interativos (gerados automaticamente)
├── project.ipynb              # Notebook exploratório original
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🗃️ Fontes de Dados

Os dados são extraídos automaticamente do **DATASUS (TabNet/SISCAN)** via web scraping e armazenados em cache CSV local:

| Fonte | Sistema | Variável | Período |
|-------|---------|----------|---------|
| População Feminina | IBGE/SVS | Projeções populacionais (25-64 anos) | 2013–2024 |
| Óbitos por C53 (CID-10) | SIM | Mortalidade por neoplasia do colo | 2013–2024 |
| Exames Citopatológicos | SISCAN | Papanicolau realizados | 2013–2024 |
| Imunizações HPV | SI-PNI | Doses aplicadas | 2013–2022 |
| Diagnósticos Histopatológicos | SISCAN | Carcinomas confirmados | 2013–2025 |

---

## ⚙️ Metodologia

### Pipeline de Dados
1. **Extração** — Scraping automatizado do TabNet com retry e cache-first
2. **Wrangling** — Transformação wide→long, merge de 5 datasets, limpeza de formatos BR
3. **Feature Engineering** — 4 KPIs calculados:

| KPI | Fórmula |
|-----|---------|
| Taxa de Mortalidade | (Óbitos / Pop. Feminina) × 100.000 |
| Cobertura de Rastreio | (Exames / Pop.) × 100 |
| Taxa de Positividade | (Diagnósticos / Exames) × 100 |
| Cobertura Vacinal | (Doses HPV / Pop.) × 100.000 |

### Análise Estatística
- **Correlação** Pearson e Spearman com heatmap dual
- **ANOVA** + Kruskal-Wallis para diferenças regionais
- **Regressão Linear** com análise de resíduos
- **PCA 3D** para redução de dimensionalidade
- **K-Means** com validação Elbow + Silhouette

---

## 📊 Visualizações

### 18 Gráficos Interativos (Plotly → HTML)

| # | Gráfico | Tipo |
|---|---------|------|
| 1 | Mapa Coroplético Animado | `px.choropleth` |
| 2 | Série Temporal + Média Móvel | `go.Scatter` |
| 3 | Bar Chart Race — Top 10 UFs | `px.bar` animado |
| 4 | Bubble Chart — Cobertura vs Mortalidade | `px.scatter` + OLS |
| 5 | Heatmap UF × Ano | `px.imshow` |
| 6 | Sunburst — Região → Estado | `px.sunburst` |
| 7 | Treemap Proporcional | `px.treemap` |
| 8 | Boxplot Dual por Região | `go.Box` |
| 9 | Painel Multi-Métrico | `make_subplots` |
| 10 | Funil de Rastreamento | `go.Funnel` |
| 11 | Small Multiples Regional | `px.line` facetado |
| 12 | Radar Chart Multidimensional | `go.Scatterpolar` |
| 13 | Correlação Pearson vs Spearman | `go.Heatmap` |
| 14 | Regressão + Resíduos | `go.Scatter` |
| 15 | PCA 3D Interativo | `px.scatter_3d` |
| 16–17 | K-Means (Elbow + Clusters) | `go.Scatter` |
| 18 | Dashboard KPI | `go.Indicator` |

### Dashboard Interativo (Dash)

App web com filtros dinâmicos por **ano**, **região**, **estado** e **métrica**, incluindo:
- 5 KPI Cards com deltas vs. ano anterior
- Storytelling textual que atualiza em tempo real
- 6 gráficos interativos sincronizados

---

## 📈 Principais Resultados

| Achado | Detalhe |
|--------|---------|
| **Correlação Negativa** | Cobertura vs. Mortalidade: ρ = −0.36 (estados com mais exames têm menos mortes) |
| **Desigualdade Regional** | Norte e Nordeste com mortalidade 2× maior que Sudeste/Sul (ANOVA p < 0.001) |
| **Regressão** | Cada 1% a mais de cobertura → −0.37 óbitos/100k (R² = 0.13) |
| **3 Perfis de UFs** | K-Means identificou clusters: baixo risco, risco moderado, alto risco |

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10+

### Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/iago7almeida/analise-exames-cancer-colo-utero.git
cd analise-exames-cancer-colo-utero

# 2. Criar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt
```

### Execução

```bash
# Pipeline completo (extrai dados, analisa, gera 18 gráficos)
python main.py

# Dashboard interativo (http://localhost:8050)
python dashboard.py
```

> **Nota:** Na primeira execução, o scraping do DATASUS leva ~10 min. Nas seguintes, o cache CSV é carregado instantaneamente.

---

## 🛠️ Tecnologias

| Categoria | Ferramentas |
|-----------|-------------|
| **Dados** | Pandas · Requests · lxml |
| **Visualização** | Plotly · Dash · Matplotlib · Seaborn |
| **Estatística** | SciPy · Statsmodels |
| **Machine Learning** | Scikit-learn (PCA, K-Means) |

---

## 📜 Licença

Este projeto está sob a licença [MIT](LICENSE).

---

*Desenvolvido por [Iago Almeida](https://github.com/iago7almeida)*
