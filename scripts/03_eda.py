"""
Aula 3 - Análise exploratória (EDA).

Perguntas respondidas aqui:
- Como o volume de tickets evolui mês a mês e dia da semana?
- Quais categorias mais aparecem?
- Como a carga está distribuída entre os responsáveis?
- Como os clientes estão classificados?

value_counts() conta ocorrências de cada valor em uma coluna.
groupby() agrupa linhas por uma coluna e permite agregar (contar, somar, etc.)
"""

import pandas as pd

df = pd.read_csv("output/tickets_limpos.csv", parse_dates=["Aberto em"])

print("=" * 60)
print("VOLUME POR MÊS")
print("=" * 60)
print(df.groupby("Ano-Mês").size())

print("\n" + "=" * 60)
print("VOLUME POR DIA DA SEMANA")
print("=" * 60)
ordem_dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
print(df["Dia da Semana"].value_counts().reindex(ordem_dias))

print("\n" + "=" * 60)
print("TOP CATEGORIAS")
print("=" * 60)
print(df["Categoria"].value_counts())

print("\n" + "=" * 60)
print("CARGA POR RESPONSÁVEL (% do total)")
print("=" * 60)
carga = df["Responsável"].value_counts(normalize=True).mul(100).round(1)
print(carga.astype(str) + "%")

print("\n" + "=" * 60)
print("CLASSIFICAÇÃO DE CLIENTE")
print("=" * 60)
print(df["Classificação Cliente"].value_counts())

print("\n" + "=" * 60)
print("URGÊNCIA")
print("=" * 60)
print(df["Urgência"].value_counts())

# Salva agregados para reaproveitar depois (gráficos, Power BI)
df.groupby("Ano-Mês").size().rename("qtd_tickets").to_csv("output/volume_mensal.csv")
df["Categoria"].value_counts().rename_axis("Categoria").reset_index(name="qtd_tickets").to_csv("output/volume_por_categoria.csv", index=False)
df["Responsável"].value_counts().rename_axis("Responsável").reset_index(name="qtd_tickets").to_csv("output/volume_por_responsavel.csv", index=False)

print("\nAgregados salvos em output/ (volume_mensal, volume_por_categoria, volume_por_responsavel)")
