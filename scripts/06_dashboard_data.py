"""
Aula 6 - Prepara um único JSON consolidado para alimentar o dashboard
interativo (Artifact) e documenta a exportação para o Power BI.
"""

import pandas as pd
import json

df = pd.read_csv("output/tickets_limpos.csv", parse_dates=["Aberto em"])

total_tickets = int(len(df))
periodo_ini = df["Aberto em"].min().strftime("%d/%m/%Y")
periodo_fim = df["Aberto em"].max().strftime("%d/%m/%Y")
dias_periodo = (df["Aberto em"].max() - df["Aberto em"].min()).days + 1
media_dia = round(total_tickets / dias_periodo, 1)

# Volume semanal
vol_semana = df.groupby(df["Aberto em"].dt.to_period("W").apply(lambda p: p.start_time)).size()
volume_semanal = [{"semana": d.strftime("%d/%m"), "qtd": int(v)} for d, v in vol_semana.items()]

# Categorias
cat = df["Categoria"].value_counts()
categorias = [{"categoria": k, "qtd": int(v)} for k, v in cat.items()]

# Responsáveis (só quem tem >0 e é atendente de fato, top 8)
resp = df["Responsável"].value_counts().head(8)
responsaveis = [{"nome": k, "qtd": int(v)} for k, v in resp.items()]

# Dia da semana
ordem_dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
dia_semana = df["Dia da Semana"].value_counts().reindex(ordem_dias).fillna(0)
dias = [{"dia": k, "qtd": int(v)} for k, v in dia_semana.items()]

# Clientes (Pareto) excluindo Alumisoft (uso interno)
df_ext = df[df["Organização"] != "Alumisoft Sistemas"]
top_clientes = df_ext["Organização"].value_counts().head(12)
total_ext = int(df_ext["Organização"].value_counts().sum())
top10_soma = int(df_ext["Organização"].value_counts().head(10).sum())
pct_top10 = round(top10_soma / total_ext * 100, 1)
clientes = [{"organizacao": k, "qtd": int(v)} for k, v in top_clientes.items()]

# Urgência geral e por categoria (para mostrar que o campo é pouco discriminante)
urgencia_geral = {k: int(v) for k, v in df["Urgência"].value_counts().items()}
pct_alta = round(df["Urgência"].value_counts(normalize=True).get("Alta", 0) * 100, 1)

# Classificação de cliente
classificacao = df["Classificação Cliente"].value_counts()
classificacao = classificacao[classificacao.index != "Não classificado"].head(6)
classif = [{"classe": k, "qtd": int(v)} for k, v in classificacao.items()]

data = {
    "resumo": {
        "total_tickets": total_tickets,
        "periodo_ini": periodo_ini,
        "periodo_fim": periodo_fim,
        "dias_periodo": dias_periodo,
        "media_dia": media_dia,
        "n_organizacoes": int(df["Organização"].nunique()),
        "pct_top10_clientes": pct_top10,
        "pct_urgencia_alta": pct_alta,
        "pct_duvidas": round(cat.get("Dúvidas", 0) / total_tickets * 100, 1),
    },
    "volume_semanal": volume_semanal,
    "categorias": categorias,
    "responsaveis": responsaveis,
    "dias_semana": dias,
    "clientes": clientes,
    "urgencia_geral": urgencia_geral,
    "classificacao": classif,
}

with open("output/dashboard_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("output/dashboard_data.json gerado")
print(json.dumps(data["resumo"], ensure_ascii=False, indent=2))
