# Urnas tardias — dashboard

Dashboard interativo para explorar quantos votos foram computados **depois das 17h** no 2º turno de 2026 (25/10), nas urnas que encerraram após as **17h45** (horário de Brasília), quando a votação foi estendida até as 19h.

Desenvolvido por **Jonnes Santos** (Arquiteto de Software).

## O que este projeto faz

- Visualiza KPIs nacionais e por filtro (UF / município)
- Gráficos de urnas estendidas por estado, horário de encerramento e ranking de municípios
- Permite baixar o CSV filtrado das seções
- Roda localmente ou no [Streamlit Community Cloud](https://share.streamlit.io)

Os números agregados (sem exterior): cerca de **7,3 mil** urnas estendidas (~1,5%) e **~5 mil** votos após as 17h nessas urnas — ordem de grandeza irrelevante frente à diferença nacional da eleição. O detalhe por UF/município fica no dashboard.

## Como rodar localmente

Pré-requisitos: Python 3.10+ e [`uv`](https://docs.astral.sh/uv/).

```sh
git clone https://github.com/Jonnes-Santos/urnas-tardias.git
cd urnas-tardias
uv run dashboard.py
```

Abre em `http://localhost:8501`.

O app lê `secoes.csv` e `municipios.csv` (já versionados). A pasta `dados/` (logs brutos) **não** entra no Git.

### Atualizar / regenerar os CSVs (opcional)

```sh
uv run crawl.py              # todas as UFs — ou: uv run crawl.py rj sp
python3 analisa.py           # regenera secoes.csv e municipios.csv
```

O crawler limita requisições ao TSE (`RPS`, padrão 10/s) e retoma de onde parou. São centenas de milhares de downloads; em conexão doméstica leva horas.

## Deploy no Streamlit Cloud

1. Abra [share.streamlit.io](https://share.streamlit.io) e autentique com GitHub
2. **New app** → repositório `Jonnes-Santos/urnas-tardias`, branch `master`
3. **Main file path:** `dashboard.py`
4. Deploy

Dependências em `requirements.txt` (`streamlit`, `pandas`, `plotly`).

## Arquivos principais

| Arquivo | Função |
|---------|--------|
| `dashboard.py` | Interface Streamlit |
| `secoes.csv` | Uma linha por urna (horários, votos tardios, classe) |
| `municipios.csv` | Municípios com urnas estendidas |
| `crawl.py` / `analisa.py` | Coleta dos logs do TSE e consolidação em CSV |
| `requirements.txt` | Dependências do dashboard |

## Critério usado na análise

- Fonte: logs de urna (`logd.dat`) publicados pelo TSE
- **Urna estendida:** encerramento depois das 17h45 (Brasília)
- **Votos tardios:** computados depois das 17h, apenas nessas urnas
- Exterior (`ZZ`) excluído (fuso por país)
- Fusos municipais inferidos pela hora típica de abertura (8h locais)

## Créditos

Pipeline original de coleta/análise dos logs do TSE: [apolinario/urnas-tardias](https://github.com/apolinario/urnas-tardias).  
Este repositório adiciona o dashboard, a experiência de navegação e o empacotamento para deploy.
