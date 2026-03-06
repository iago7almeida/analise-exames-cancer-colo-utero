# Análise de Dados: Prevenção e Mortalidade do Câncer de Colo de Útero no Brasil

![Status](https://img.shields.io/badge/Status-Concluído-green) ![Python](https://img.shields.io/badge/Language-Python-blue)

## 📌 Visão Geral do Projeto
O câncer de colo de útero é uma das principais causas de morte entre mulheres no Brasil, apesar de ser altamente prevenível. Este projeto utiliza Engenharia e Análise de Dados para investigar a eficiência das políticas públicas de rastreamento (Papanicolau) e prevenção primária (Vacinação HPV).

O objetivo é responder: **A baixa cobertura de exames e o abandono vacinal estão correlacionados com as taxas de mortalidade nos estados brasileiros?**

## 🗂️ Coleta de Dados
Os dados foram extraídos diretamente do **DATASUS (Tabnet)** utilizando scripts em Python automatizados, sem download manual de arquivos CSV.

* **Fonte 1 (Mortalidade):** Sistema de Informações sobre Mortalidade (SIM) - CID-10 C53.
* **Fonte 2 (População):** IBGE (Projeções Populacionais via Tabnet).
* **Fonte 3 (Rastreamento):** SISCAN/SIA (Exames Citopatológicos).
* **Fonte 4 (Imunização):** SI-PNI (Doses de Vacina HPV Quadrivalente).

**Tecnologias:** `Python`, `Pandas`, `Requests` (para Web Scraping do Tabnet), `Regular Expressions` (Regex), `Seaborn/Matplotlib`.

## ⚙️ Metodologia e Modelagem
1.  **Engenharia de Dados:** Criação de robôs (`requests`) para enviar payloads ao servidor do DATASUS e estruturar as respostas HTML em DataFrames utilizáveis.
2.  **Data Wrangling:** Transformação de dados "Wide" (anos em colunas) para "Long" (anos em linhas), tratamento de nulos e padronização de chaves (UF).
3.  **Criação de KPIs:**
    * *Taxa de Mortalidade:* (Óbitos / População Feminina) * 100k.
    * *Taxa de Abandono Vacinal:* ((Dose 1 - Dose 2) / Dose 1) * 100.
    * *Cobertura de Rastreio (Proxy):* Exames realizados vs. População Alvo.

## 📊 Principais Insights e Conclusões

### 1. Desigualdade Regional na Mortalidade
Identificamos "Hotspots" de mortalidade nas regiões Norte e Nordeste. Estados como Amazonas apresentam taxas significativamente superiores à média nacional.

### 2. O Gargalo da Vacinação (HPV)
A análise revelou uma taxa de abandono vacinal preocupante. Em alguns estados, uma boa parte das mulheres recebem a primeira dose, mas não retornam para a segunda, comprometendo a imunização, observado pela correlação positivtiva entre imunizações e óbitos.

### 3. Correlação Rastreio x Óbitos
Observou-se uma tendência onde estados com menor histórico de cobertura de exames Papanicolau tendem a apresentar as maiores taxas de mortalidade, reforçando a importância da busca ativa por pacientes.

## 📈 Visualizações
Os gráficos detalhados e o código da análise estão disponíveis no notebook principal.

[**Acesse o Dashboard Interativo aqui**](https://lookerstudio.google.com/reporting/fb59fc99-fc3f-43c1-a9dd-cf25f47ed02f/page/xwViF)

---
*Autor: Iago Almeida*
