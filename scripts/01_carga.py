"""
Aula 1 - Carga (via API do Movidesk) e primeira exploração dos dados.

Antes era: ler o Excel exportado manualmente.
Agora: busca os tickets direto na API do Movidesk e monta o mesmo
formato de tabela que o Excel tinha, para o resto do pipeline (02 em
diante) não precisar mudar nada.

Configuração necessária (uma vez só): copie .env.example para .env e
cole o token da API do Movidesk. Veja o README.md para o passo a passo
de onde encontrar esse token.

Objetivo (igual antes):
- quantas linhas/colunas?
- quais tipos de dado em cada coluna?
- quantos valores nulos (faltantes)?
- qual o período coberto?
"""

import os
from datetime import datetime, timedelta, timezone

import pandas as pd
from dotenv import load_dotenv

import movidesk_client as movidesk

load_dotenv()

ARQUIVO_CACHE = "data/tickets_movidesk_raw.csv"

# Janela de datas: fixe MOVIDESK_DATA_INICIO / MOVIDESK_DATA_FIM (formato
# YYYY-MM-DD) no .env para reproduzir um período específico. Sem isso, o
# padrão é "últimos 365 dias" (1 ano de operação de suporte). A rota
# /tickets só cobre os últimos 90 dias por si só; movidesk_client.py
# complementa automaticamente com /tickets/past para o restante do ano.
_data_fim_env = os.environ.get("MOVIDESK_DATA_FIM")
_data_inicio_env = os.environ.get("MOVIDESK_DATA_INICIO")
data_fim = datetime.fromisoformat(_data_fim_env) if _data_fim_env else datetime.now(timezone.utc)
data_inicio = (
    datetime.fromisoformat(_data_inicio_env) if _data_inicio_env else data_fim - timedelta(days=365)
)

print("=" * 60)
print("BUSCANDO TICKETS NA API DO MOVIDESK")
print("=" * 60)
print(f"Período (createdDate): {data_inicio:%Y-%m-%d} até {data_fim:%Y-%m-%d}")

tickets = movidesk.buscar_tickets(data_inicio, data_fim)
print(f"\nTotal de tickets recebidos: {len(tickets)}")

print("\nBuscando classificação das organizações (para 'Cliente: Classificação')...")
classificacao_por_org = movidesk.buscar_classificacao_organizacoes()
print(f"Organizações carregadas: {len(classificacao_por_org)}")

MAPA_TIPO = {1: "Interno", 2: "Público"}


def montar_cliente_completo(ticket):
    clientes = ticket.get("clients") or []
    if not clientes:
        return pd.NA
    cliente = clientes[0]
    org = cliente.get("organization")
    if org and org.get("businessName"):
        return f"{org['businessName']} » {cliente.get('businessName', '')}"
    return cliente.get("businessName")


def montar_classificacao(ticket):
    clientes = ticket.get("clients") or []
    if not clientes:
        return pd.NA
    org = clientes[0].get("organization")
    if not org:
        return pd.NA
    return classificacao_por_org.get(org.get("id"))


linhas = []
for t in tickets:
    linhas.append(
        {
            "Número": t.get("id"),
            "Tipo": MAPA_TIPO.get(t.get("type")),
            "Assunto": t.get("subject"),
            "Aberto em": t.get("createdDate"),
            "Cliente (Completo)": montar_cliente_completo(t),
            "Responsável": (t.get("owner") or {}).get("businessName"),
            "Categoria": t.get("category"),
            "Urgência": t.get("urgency"),
            "Status": t.get("status"),
            "Justificativa": t.get("justification"),
            "Cliente: Classificação (Organização)": montar_classificacao(t),
            "Serviço (2º Nível)": t.get("serviceSecondLevel"),
        }
    )

df = pd.DataFrame(linhas)

# createdDate vem em UTC da API; convertemos para o horário de Brasília
# (fuso em que os tickets de fato são abertos) e descartamos o timezone
# para manter o mesmo formato "ingênuo" que o Excel tinha.
df["Aberto em"] = (
    pd.to_datetime(df["Aberto em"], utc=True)
    .dt.tz_convert("America/Sao_Paulo")
    .dt.tz_localize(None)
)

os.makedirs("data", exist_ok=True)
df.to_csv(ARQUIVO_CACHE, index=False, encoding="utf-8-sig")
print(f"\nCache salvo em {ARQUIVO_CACHE} — as próximas etapas (02 em diante) leem daqui.")

print("\n" + "=" * 60)
print("DIMENSÕES DO DATASET")
print("=" * 60)
print(f"Linhas (tickets): {df.shape[0]}")
print(f"Colunas: {df.shape[1]}")

print("\n" + "=" * 60)
print("COLUNAS E TIPOS")
print("=" * 60)
print(df.dtypes)

print("\n" + "=" * 60)
print("VALORES NULOS POR COLUNA")
print("=" * 60)
print(df.isna().sum())

print("\n" + "=" * 60)
print("PERÍODO COBERTO")
print("=" * 60)
print(f"De {df['Aberto em'].min()} até {df['Aberto em'].max()}")

print("\n" + "=" * 60)
print("AMOSTRA (5 primeiras linhas)")
print("=" * 60)
print(df.head())
