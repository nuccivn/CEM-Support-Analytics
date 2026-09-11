# CEM Support Analytics

Análise dos chamados de suporte do produto CEM (Alumisoft): carga e limpeza dos
dados, exploração, cruzamentos e um painel executivo interativo — tudo em
Python/pandas, sem Power BI.

**Painel ao vivo:** https://supportanalytics.vercel.app

## O que tem aqui

- `scripts/movidesk_client.py` — cliente HTTP para a API do Movidesk (busca
  tickets e a classificação das organizações, com rate limiting e paginação).
- `scripts/01_carga.py` a `scripts/06_dashboard_data.py` — pipeline em ordem:
  carga (via API) → limpeza → EDA → cruzamentos (Pareto) → gráficos → JSON
  consolidado.
- `data/tickets_movidesk_raw.csv` — cache local gerado pelo `01_carga.py` com
  os tickets buscados na API (é o que `02_limpeza.py` em diante consome).
  Fora do git (`.gitignore`) — é recriado a cada execução.
- `data/TicketSuporteCem.xlsx` — base bruta antiga (Excel exportado
  manualmente). Mantida só como referência histórica; o pipeline não usa
  mais este arquivo, a fonte agora é a API do Movidesk.
- `output/` — CSVs agregados, gráficos PNG e `dashboard_data.json` (o que
  alimenta o painel).
- `index.html` — o painel executivo (HTML/CSS/JS puro, sem build, sem
  dependências) — é o que vai pro ar na Vercel.
- `api/refresh.js` e `api/refresh-status.js` — funções serverless da Vercel
  que disparam o pipeline no GitHub Actions e acompanham o andamento (ver
  "Atualização ao carregar a página" abaixo).

## Configurar o acesso à API do Movidesk (uma vez só)

1. Copie `.env.example` para `.env`.
2. No Movidesk: ícone de engrenagem (Configurações) → **Conta** →
   **Parâmetros** → aba **Ambiente** → role até a seção **API** → botão
   **"Gerar nova chave"** (se ainda não existir uma).
3. Cole a chave em `.env`, na variável `MOVIDESK_TOKEN`.

⚠️ Gerar uma chave nova invalida a anterior em qualquer lugar que já a use.
O `.env` já está no `.gitignore` — nunca commite o token.

Três formas de controlar o período buscado, em ordem de prioridade:
1. `MOVIDESK_DATA_INICIO` / `MOVIDESK_DATA_FIM` (formato `YYYY-MM-DD`) fixam
   datas exatas.
2. `MOVIDESK_DIAS` (inteiro) busca "os últimos N dias a partir de agora" — é
   o que o seletor de período do painel usa (30/90/180/270/365).
3. Sem nada disso, o padrão é 365 dias (1 ano).

A rota `/tickets` da Movidesk só cobre os últimos 90 dias por conta própria
— o `movidesk_client.py` já complementa automaticamente com a rota
`/tickets/past` para cobrir o restante do período pedido.

A API da Movidesk limita a 10 requisições/minuto; o `movidesk_client.py` já
respeita esse limite sozinho (a carga de 1 ano inteiro pode levar vários
minutos, dependendo do volume de tickets).

## Atualização ao carregar a página

Toda vez que alguém abre o painel, o `index.html` chama `api/refresh.js`
(função serverless da Vercel), que dispara o workflow
`.github/workflows/atualizar-dados.yml` no GitHub Actions — o mesmo pipeline
completo (`01_carga.py` a `06_dashboard_data.py`), que busca os tickets na
Movidesk e faz commit + push do `output/` atualizado (o que por sua vez
dispara um novo deploy na Vercel). A página mostra "Atualizando..." e só
desenha o painel quando essa execução termina — como a Movidesk limita a
10 requisições/minuto, isso pode levar alguns minutos. Se a atualização
falhar ou demorar demais, o painel cai de volta pros últimos dados
disponíveis, com um aviso.

O seletor de período no topo do painel (1/3/6/9 meses ou 1 ano) manda o
período escolhido pro `api/refresh.js`, que repassa como input do
`workflow_dispatch` (`dias`) — períodos menores buscam bem mais rápido, já
que ficam dentro da janela de 90 dias e nem precisam da rota
`/tickets/past`. A última escolha fica salva no navegador (localStorage) e
volta a ser usada no próximo carregamento.

Qualquer pessoa com o link do painel pode disparar uma atualização (não há
login) — se duas pessoas carregarem a página ao mesmo tempo, as execuções
ficam em fila no GitHub Actions (`concurrency` no workflow) em vez de rodar
em paralelo.

Ainda existe um agendamento diário (07h, horário de Brasília) como
fallback, caso o painel fique um tempo sem ser acessado.

Configuração necessária (uma vez só):

1. No GitHub: **Settings** → **Secrets and variables** → **Actions** →
   **New repository secret** → cadastre `MOVIDESK_TOKEN` com o mesmo token
   usado no `.env` local.
2. Crie um token de acesso do GitHub só pra esse repositório: **Settings da
   sua conta** → **Developer settings** → **Personal access tokens** →
   **Fine-grained tokens** → **Generate new token**, restrito a este
   repositório, com permissão **Actions: Read and write**.
3. Na Vercel: **Project Settings** → **Environment Variables** → adicione
   `GH_ACTIONS_TOKEN` com o valor desse token.

O workflow também pode ser disparado manualmente pela aba **Actions** →
**Atualizar dados do painel** → **Run workflow**.

## Rodar o pipeline localmente

```bash
pip install -r requirements.txt
python scripts/01_carga.py       # busca os tickets na API do Movidesk
python scripts/02_limpeza.py
python scripts/03_eda.py
python scripts/04_cruzamentos.py
python scripts/05_graficos.py
python scripts/06_dashboard_data.py
```

Cada script consome o resultado do anterior e grava em `output/`. O
`index.html` busca os dados direto de `output/dashboard_data.json` via
`fetch` (não há mais nada pra colar manualmente) — então basta rodar o
pipeline de novo pra atualizar o painel.

## Ver o painel localmente

Como o `index.html` busca `output/dashboard_data.json` via `fetch`, abrir o
arquivo direto (`file://`) não funciona — o navegador bloqueia isso por
CORS. Sirva a pasta por HTTP:

```bash
python -m http.server 8000
```

e acesse `http://localhost:8000`.

## Deploy

Projeto `supportanalytics` na Vercel, conectado ao repositório GitHub
`nuccivn/CEM-Support-Analytics` (sem build step — framework preset "Other").
Qualquer push na branch `main` atualiza o painel automaticamente.

⚠️ Se um dia o site parecer "travado" num snapshot antigo mesmo após vários
pushes, o primeiro lugar a checar é se o projeto na Vercel ainda está
conectado a este repositório (Project Settings → Git) — já aconteceu de
ele estar apontando pra um repo homônimo errado, e nesse caso nenhum push
aqui gera deploy nenhum.

## Principais achados (snapshot 09/06 a 09/09/2026)

- Dúvidas de uso são 48,4% dos chamados — maior espaço para autoatendimento.
- 83,9% chegam marcados como "Alta" urgência — o campo está pouco discriminante.
- Carteira pulverizada: top 10 clientes = 10,6% do volume, entre 802 organizações.
- Operação concentrada em dias úteis (fins de semana ≈ 0,3% do volume).
