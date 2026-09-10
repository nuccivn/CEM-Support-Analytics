# CEM Support Analytics

Análise dos chamados de suporte do produto CEM (Alumisoft): carga e limpeza dos
dados, exploração, cruzamentos e um painel executivo interativo — tudo em
Python/pandas, sem Power BI.

**Painel ao vivo:** _(adicionar link da Vercel aqui depois do deploy)_

## O que tem aqui

- `data/TicketSuporteCem.xlsx` — base bruta de tickets (fonte).
- `scripts/01_carga.py` a `scripts/06_dashboard_data.py` — pipeline em ordem:
  carga → limpeza → EDA → cruzamentos (Pareto) → gráficos → JSON consolidado.
- `output/` — CSVs agregados, gráficos PNG e `dashboard_data.json` (o que
  alimenta o painel).
- `index.html` — o painel executivo (HTML/CSS/JS puro, sem build, sem
  dependências) — é o que vai pro ar na Vercel.

## Rodar o pipeline localmente

```bash
pip install -r requirements.txt
python scripts/01_carga.py
python scripts/02_limpeza.py
python scripts/03_eda.py
python scripts/04_cruzamentos.py
python scripts/05_graficos.py
python scripts/06_dashboard_data.py
```

Cada script consome o resultado do anterior e grava em `output/`. Se a base
de tickets mudar, é só rodar de novo — os números do `index.html` hoje estão
com um snapshot fixo desses dados; para atualizar o painel, os valores em
`DATA` dentro do `index.html` precisam refletir o novo
`output/dashboard_data.json`.

## Ver o painel localmente

`index.html` é estático — basta abrir o arquivo no navegador, ou:

```bash
python -m http.server 8000
```

e acessar `http://localhost:8000`.

## Deploy

Importado direto do GitHub na Vercel (sem build step — framework preset
"Other"). Qualquer push na branch principal atualiza o painel automaticamente.

## Principais achados (snapshot 09/06 a 09/09/2026)

- Dúvidas de uso são 48,4% dos chamados — maior espaço para autoatendimento.
- 83,9% chegam marcados como "Alta" urgência — o campo está pouco discriminante.
- Carteira pulverizada: top 10 clientes = 10,6% do volume, entre 802 organizações.
- Operação concentrada em dias úteis (fins de semana ≈ 0,3% do volume).
