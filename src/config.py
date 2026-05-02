"""
Configurações globais do projeto.
Constantes, caminhos, paletas de cores e mapeamentos.
"""
import os

# ==============================================================================
# Caminhos
# ==============================================================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==============================================================================
# Tema Visual
# ==============================================================================
PLOTLY_TEMPLATE = 'plotly_dark'

CORES = {
    'primaria': '#E63946',
    'secundaria': '#457B9D',
    'terciaria': '#2A9D8F',
    'alerta': '#F4A261',
    'fundo': '#1A1A2E',
    'plot_bg': '#16213E',
    'texto': '#E0E0E0',
}

PALETA_REGIOES = {
    'Norte': '#E63946',
    'Nordeste': '#F4A261',
    'Sudeste': '#457B9D',
    'Sul': '#2A9D8F',
    'Centro-Oeste': '#A855F7',
}

# ==============================================================================
# Mapeamento de Estados
# ==============================================================================
SIGLAS = {
    'Rondônia': 'RO', 'Acre': 'AC', 'Amazonas': 'AM', 'Roraima': 'RR',
    'Pará': 'PA', 'Amapá': 'AP', 'Tocantins': 'TO', 'Maranhão': 'MA',
    'Piauí': 'PI', 'Ceará': 'CE', 'Rio Grande do Norte': 'RN',
    'Paraíba': 'PB', 'Pernambuco': 'PE', 'Alagoas': 'AL', 'Sergipe': 'SE',
    'Bahia': 'BA', 'Minas Gerais': 'MG', 'Espírito Santo': 'ES',
    'Rio de Janeiro': 'RJ', 'São Paulo': 'SP', 'Paraná': 'PR',
    'Santa Catarina': 'SC', 'Rio Grande do Sul': 'RS',
    'Mato Grosso do Sul': 'MS', 'Mato Grosso': 'MT', 'Goiás': 'GO',
    'Distrito Federal': 'DF',
}

REGIOES = {
    'Norte': ['Acre', 'Amazonas', 'Roraima', 'Rondônia', 'Pará', 'Amapá', 'Tocantins'],
    'Nordeste': ['Maranhão', 'Piauí', 'Ceará', 'Rio Grande do Norte', 'Paraíba',
                 'Pernambuco', 'Alagoas', 'Sergipe', 'Bahia'],
    'Sudeste': ['Minas Gerais', 'Espírito Santo', 'Rio de Janeiro', 'São Paulo'],
    'Sul': ['Paraná', 'Santa Catarina', 'Rio Grande do Sul'],
    'Centro-Oeste': ['Mato Grosso do Sul', 'Mato Grosso', 'Goiás', 'Distrito Federal'],
}

# ==============================================================================
# Payloads do DATASUS (para Web Scraping)
# ==============================================================================
HEADERS_TABNET = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

PAYLOAD_POPULACAO = {
    'url': 'http://tabnet.datasus.gov.br/cgi/tabcgi.exe?ibge/cnv/popsvs2024br.def',
    'data': "Linha=Unidade_da_Federa%E7%E3o&Coluna=Ano&Incremento=Popula%E7%E3o_residente&Arquivos=pop24.dbf&Arquivos=pop23.dbf&Arquivos=pop22.dbf&Arquivos=pop21.dbf&Arquivos=pop20.dbf&Arquivos=pop19.dbf&Arquivos=pop18.dbf&Arquivos=pop17.dbf&Arquivos=pop16.dbf&Arquivos=pop15.dbf&Arquivos=pop14.dbf&Arquivos=pop13.dbf&SRegi%E3o=TODAS_AS_CATEGORIAS__&pesqmes2=Digite+o+texto+e+ache+f%E1cil&SUnidade_da_Federa%E7%E3o=TODAS_AS_CATEGORIAS__&pesqmes3=Digite+o+texto+e+ache+f%E1cil&SMunic%EDpio=TODAS_AS_CATEGORIAS__&pesqmes4=Digite+o+texto+e+ache+f%E1cil&SCapital=TODAS_AS_CATEGORIAS__&pesqmes5=Digite+o+texto+e+ache+f%E1cil&SRegi%E3o_de_Sa%FAde_%28CIR%29=TODAS_AS_CATEGORIAS__&pesqmes6=Digite+o+texto+e+ache+f%E1cil&SMacrorregi%E3o_de_Sa%FAde=TODAS_AS_CATEGORIAS__&pesqmes7=Digite+o+texto+e+ache+f%E1cil&SMicrorregi%E3o_IBGE=TODAS_AS_CATEGORIAS__&pesqmes8=Digite+o+texto+e+ache+f%E1cil&SRegi%E3o_Metropolitana_-_RIDE=TODAS_AS_CATEGORIAS__&pesqmes9=Digite+o+texto+e+ache+f%E1cil&SMacrorregi%E3o_PNDR=TODAS_AS_CATEGORIAS__&SAmaz%F4nia_Legal=TODAS_AS_CATEGORIAS__&SSemi%E1rido=TODAS_AS_CATEGORIAS__&SFaixa_de_Fronteira=TODAS_AS_CATEGORIAS__&SZona_de_Fronteira=TODAS_AS_CATEGORIAS__&SMunic%EDpio_de_extrema_pobreza=TODAS_AS_CATEGORIAS__&SSexo=2&pesqmes16=Digite+o+texto+e+ache+f%E1cil&SFaixa_Et%E1ria_1=3&SFaixa_Et%E1ria_1=4&SFaixa_Et%E1ria_1=5&SFaixa_Et%E1ria_1=6&SFaixa_Et%E1ria_1=7&SFaixa_Et%E1ria_1=8&SFaixa_Et%E1ria_1=9&SFaixa_Et%E1ria_1=10&SFaixa_Et%E1ria_1=11&pesqmes17=Digite+o+texto+e+ache+f%E1cil&SFaixa_Et%E1ria_2=TODAS_AS_CATEGORIAS__&pesqmes18=Digite+o+texto+e+ache+f%E1cil&SIdade_simples=TODAS_AS_CATEGORIAS__&formato=table&mostre=Mostra",
}

PAYLOAD_OBITOS = {
    'url': 'http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sim/cnv/obt10uf.def',
    'data': "Linha=Unidade_da_Federa%E7%E3o&Coluna=Ano_do_%D3bito&Incremento=%D3bitos_p%2FOcorr%EAnc&Arquivos=obtuf24.dbf&Arquivos=obtuf23.dbf&Arquivos=obtuf22.dbf&Arquivos=obtuf21.dbf&Arquivos=obtuf20.dbf&Arquivos=obtuf19.dbf&Arquivos=obtuf18.dbf&Arquivos=obtuf17.dbf&Arquivos=obtuf16.dbf&Arquivos=obtuf15.dbf&Arquivos=obtuf14.dbf&Arquivos=obtuf13.dbf&SRegi%E3o=TODAS_AS_CATEGORIAS__&pesqmes2=Digite+o+texto+e+ache+f%E1cil&SUnidade_da_Federa%E7%E3o=TODAS_AS_CATEGORIAS__&pesqmes3=&pesqmes4=Digite+o+texto+e+ache+f%E1cil&SGrupo_CID-10=TODAS_AS_CATEGORIAS__&pesqmes5=&SCategoria_CID-10=219&pesqmes6=Digite+o+texto+e+ache+f%E1cil&SCausa_-_CID-BR-10=TODAS_AS_CATEGORIAS__&SCausa_mal_definidas=TODAS_AS_CATEGORIAS__&pesqmes8=Digite+o+texto+e+ache+f%E1cil&SFaixa_Et%E1ria=TODAS_AS_CATEGORIAS__&pesqmes9=Digite+o+texto+e+ache+f%E1cil&SFaixa_Et%E1ria_OPS=TODAS_AS_CATEGORIAS__&pesqmes10=Digite+o+texto+e+ache+f%E1cil&SFaixa_Et%E1ria_det=TODAS_AS_CATEGORIAS__&SFx.Et%E1ria_Menor_1A=TODAS_AS_CATEGORIAS__&SSexo=TODAS_AS_CATEGORIAS__&SCor%2Fra%E7a=TODAS_AS_CATEGORIAS__&SEscolaridade=TODAS_AS_CATEGORIAS__&SEstado_civil=TODAS_AS_CATEGORIAS__&SLocal_ocorr%EAncia=TODAS_AS_CATEGORIAS__&formato=table&mostre=Mostra",
}

PAYLOAD_IMUNIZACOES = {
    'url': 'http://tabnet.datasus.gov.br/cgi/webtabx.exe?bd_pni/dpnibr.def',
    'data': "Linha=Unidade+da+Federa%E7%E3o%7CFATO.CO_UF%7C1%7Cterritorio%5Cbr_uf.cnv&Coluna=Ano%7CCO_ANO%7C1%7CBD_pni%5CCNV%5CANO.CNV&Incremento=Doses_aplicadas%7CQT_DOSE&PAno=2022%7C2022%7C4&PAno=2021%7C2021%7C4&PAno=2020%7C2020%7C4&PAno=2019%7C2019%7C4&PAno=2018%7C2018%7C4&PAno=2017%7C2017%7C4&PAno=2016%7C2016%7C4&PAno=2015%7C2015%7C4&PAno=2014%7C2014%7C4&PAno=2013%7C2013%7C4&SRegi%E3o=TODAS_AS_CATEGORIAS__&pesqmes2=Digite+o+texto+e+ache+f%E1cil&SUnidade+da+Federa%E7%E3o=TODAS_AS_CATEGORIAS__&pesqmes3=Digite+o+texto+e+ache+f%E1cil&SMunic%EDpio=TODAS_AS_CATEGORIAS__&pesqmes4=Digite+o+texto+e+ache+f%E1cil&SCapital=TODAS_AS_CATEGORIAS__&pesqmes5=Digite+o+texto+e+ache+f%E1cil&SRegi%E3o+de+Sa%FAde+%28CIR%29=TODAS_AS_CATEGORIAS__&pesqmes6=Digite+o+texto+e+ache+f%E1cil&SMacrorregi%E3o+de+Sa%FAde=TODAS_AS_CATEGORIAS__&pesqmes7=Digite+o+texto+e+ache+f%E1cil&SMicrorregi%E3o+IBGE=TODAS_AS_CATEGORIAS__&pesqmes8=Digite+o+texto+e+ache+f%E1cil&SRegi%E3o+Metropolitana+-+RIDE=TODAS_AS_CATEGORIAS__&pesqmes9=Digite+o+texto+e+ache+f%E1cil&STerrit%F3rio+da+Cidadania=TODAS_AS_CATEGORIAS__&pesqmes10=Digite+o+texto+e+ache+f%E1cil&SMesorregi%E3o+PNDR=TODAS_AS_CATEGORIAS__&SAmaz%F4nia+Legal=TODAS_AS_CATEGORIAS__&SSemi%E1rido=TODAS_AS_CATEGORIAS__&SFaixa+de+Fronteira=TODAS_AS_CATEGORIAS__&SZona+de+Fronteira=TODAS_AS_CATEGORIAS__&SMunic%EDpio+de+extrema+pobreza=TODAS_AS_CATEGORIAS__&pesqmes16=&SImunobiol%F3gicos=HPV+Quadrivalente+-+Feminino%7C93%7C2&SImunobiol%F3gicos=HPV+Quadrivalente+-+Masculino%7C94%7C2&SImunobiol%F3gicos=HPV%7C84%7C2&pesqmes17=Digite+o+texto+e+ache+f%E1cil&SDose=TODAS_AS_CATEGORIAS__&pesqmes18=Digite+o+texto+e+ache+f%E1cil&SAno%2Fm%EAs=TODAS_AS_CATEGORIAS__&pesqmes20=Digite+o+texto+e+ache+f%E1cil&SFaixa_Et%E1ria=TODAS_AS_CATEGORIAS__&nomedef=bd_pni%2Fdpnibr.def&grafico=",
}

PAYLOAD_DIAGNOSTICOS = {
    'url': 'http://tabnet.datasus.gov.br/cgi/webtabx.exe?siscan/histo_pacbr.def',
    'data': "Linha=UF+de+residencia%7CCO_UF_RESIDENCIA%7C1%7Cterritorio%5Cbr_uf.cnv&Coluna=Ano+resultado%7CNU_ANO_RESULTADO%7C1%7CSISCAN%5Cano.cnv&Incremento=Pacientes+distintos%7C%3Dcount%28distinct+co_paciente%29&PAno+competencia=2025%7C2025%7C4&PAno+competencia=2024%7C2024%7C4&PAno+competencia=2023%7C2023%7C4&PAno+competencia=2022%7C2022%7C4&PAno+competencia=2021%7C2021%7C4&PAno+competencia=2020%7C2020%7C4&PAno+competencia=2019%7C2019%7C4&PAno+competencia=2018%7C2018%7C4&PAno+competencia=2017%7C2017%7C4&PAno+competencia=2016%7C2016%7C4&PAno+competencia=2015%7C2015%7C4&PAno+competencia=2014%7C2014%7C4&PAno+competencia=2013%7C2013%7C4&pesqmes1=Digite+o+texto+e+ache+f%E1cil&SUF+de+residencia=TODAS_AS_CATEGORIAS__&pesqmes2=Digite+o+texto+e+ache+f%E1cil&SMunic.de+residencia=TODAS_AS_CATEGORIAS__&pesqmes3=Digite+o+texto+e+ache+f%E1cil&SAno+resultado=TODAS_AS_CATEGORIAS__&SLaudo+histopatol%F3gico=Carcinoma+Epidermoide%7C01%7C2&SLaudo+histopatol%F3gico=Adenocarcinoma+invasor%7C02%7C2&SLaudo+histopatol%F3gico=Adenocarcinoma+in+situ%7C03%7C2&SLaudo+histopatol%F3gico=NIC+III+%2F+Carc.+in+situ%7C04%7C2&XRa%E7a%2FCor=TODAS_AS_CATEGORIAS__&XSexo=TODAS_AS_CATEGORIAS__&pesqmes8=Digite+o+texto+e+ache+f%E1cil&XFaixa+et%E1ria=TODAS_AS_CATEGORIAS__&XEscolaridade=TODAS_AS_CATEGORIAS__&XTipo+Encaminhamento=TODAS_AS_CATEGORIAS__&XTipo+de+procedimento+%28mat.+enviado%29=TODAS_AS_CATEGORIAS__&XAdequabilidade=Satisfat%F3rio%7C01%7C2&nomedef=siscan%2Fhisto_pacbr.def&grafico=",
}

PAYLOAD_EXAMES_BASE = "Linha=UF+de+residencia%7CCO_UF_RESIDENCIA%7C1%7Cterritorio%5Cbr_uf.cnv&Coluna=Ano+competencia%7CCO_ANO_LIBERACAO%7C1%7CCITO%5Cano.cnv&Incremento=Pacientes+distintos%7C%3Dcount%28distinct+co_paciente%29"
PAYLOAD_EXAMES_FILTROS = "&pesqmes1=Digite+o+texto+e+ache+f%E1cil&SUF+de+residencia=TODAS_AS_CATEGORIAS__&pesqmes2=Digite+o+texto+e+ache+f%E1cil&SMunic.de+residencia=TODAS_AS_CATEGORIAS__&XSexo=TODAS_AS_CATEGORIAS__&XRa%E7a%2FCor=TODAS_AS_CATEGORIAS__&pesqmes6=Digite+o+texto+e+ache+f%E1cil&XFaixa+et%E1ria=Entre+10+a+14+anos%7C010-014%7C3&XFaixa+et%E1ria=Entre+15+a+19+anos%7C015-019%7C3&XFaixa+et%E1ria=Entre+20+a+24+anos%7C020-024%7C3&XFaixa+et%E1ria=Entre+25+a+29+anos%7C025-029%7C3&XFaixa+et%E1ria=Entre+30+a+34+anos%7C030-034%7C3&XFaixa+et%E1ria=Entre+35+a+39+anos%7C035-039%7C3&XFaixa+et%E1ria=Entre+40+a+44+anos%7C040-044%7C3&XFaixa+et%E1ria=Entre+45+a+49+anos%7C045-049%7C3&XFaixa+et%E1ria=Entre+50+a+54+anos%7C050-054%7C3&XFaixa+et%E1ria=Entre+55+a+59+anos%7C055-059%7C3&XFaixa+et%E1ria=Entre+60+a+64+anos%7C060-064%7C3&XFaixa+et%E1ria=Entre+65+a+69+anos%7C065-069%7C3&XFaixa+et%E1ria=Entre+70+a+74+anos%7C070-074%7C3&XFaixa+et%E1ria=Entre+75+a+79+anos%7C075-079%7C3&XFaixa+et%E1ria=Acima+de+79+anos%7C080-120%7C3&XEscolaridade=TODAS_AS_CATEGORIAS__&XCitologia+anterior=TODAS_AS_CATEGORIAS__&XAdequabilidade=TODAS_AS_CATEGORIAS__&pesqmes10=Digite+o+texto+e+ache+f%E1cil&XLaudo+Citopatol%F3gico=TODAS_AS_CATEGORIAS__&XPres.+Cel.+Endometri=TODAS_AS_CATEGORIAS__&XRepresent.+ZT=TODAS_AS_CATEGORIAS__&XMotivo+do+exame=TODAS_AS_CATEGORIAS__&XInspe%E7%E3o+do+colo=TODAS_AS_CATEGORIAS__&pesqmes15=Digite+o+texto+e+ache+f%E1cil&XAno+Resultado=TODAS_AS_CATEGORIAS__&nomedef=SISCAN%2Fcito_colo_pacbr.def&grafico="
