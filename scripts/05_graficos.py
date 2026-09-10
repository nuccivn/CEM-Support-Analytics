"""
Aula 5 - Gráficos para apresentação.

Cada gráfico responde a uma pergunta de negócio específica.
Salvamos como PNG em output/graficos/ para colar direto num slide.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs("output/graficos", exist_ok=True)
df = pd.read_csv("output/tickets_limpos.csv", parse_dates=["Aberto em"])

plt.rcParams["figure.figsize"] = (9, 5)
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False

# 1) Volume de tickets por semana (mais granular que por mês, mostra tendência real)
volume_semanal = df.groupby(df["Aberto em"].dt.to_period("W").astype(str)).size()
fig, ax = plt.subplots()
volume_semanal.plot(kind="line", marker="o", ax=ax, color="#2563eb")
ax.set_title("Volume de tickets por semana")
ax.set_xlabel("")
ax.set_ylabel("Tickets")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("output/graficos/01_volume_semanal.png", dpi=150)
plt.close()

# 2) Top categorias
top_cat = df["Categoria"].value_counts().head(8)
fig, ax = plt.subplots()
top_cat.sort_values().plot(kind="barh", ax=ax, color="#2563eb")
ax.set_title("Top 8 categorias de chamado")
ax.set_xlabel("Tickets")
plt.tight_layout()
plt.savefig("output/graficos/02_top_categorias.png", dpi=150)
plt.close()

# 3) Carga por responsável
carga = df["Responsável"].value_counts().head(10)
fig, ax = plt.subplots()
carga.sort_values().plot(kind="barh", ax=ax, color="#16a34a")
ax.set_title("Volume de tickets por responsável (top 10)")
ax.set_xlabel("Tickets")
plt.tight_layout()
plt.savefig("output/graficos/03_carga_responsavel.png", dpi=150)
plt.close()

# 4) Curva de Pareto - concentração de clientes (excluindo Alumisoft, que é uso interno)
volume_cliente = df[df["Organização"] != "Alumisoft Sistemas"]["Organização"].value_counts()
top30 = volume_cliente.head(30)
acumulado = (top30.cumsum() / volume_cliente.sum() * 100)
fig, ax1 = plt.subplots()
ax1.bar(range(len(top30)), top30.values, color="#2563eb")
ax1.set_ylabel("Tickets")
ax1.set_xticks([])
ax2 = ax1.twinx()
ax2.plot(range(len(top30)), acumulado.values, color="#dc2626", marker="o", markersize=3)
ax2.set_ylabel("% acumulado")
ax2.axhline(80, color="gray", linestyle="--", linewidth=1)
ax1.set_title("Pareto: top 30 clientes por volume de chamados")
plt.tight_layout()
plt.savefig("output/graficos/04_pareto_clientes.png", dpi=150)
plt.close()

print("4 gráficos salvos em output/graficos/")
