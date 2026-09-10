"""
Aula 4 - Cruzamentos e análise de Pareto (80/20).

- Pareto de clientes: poucos clientes concentram a maioria dos chamados?
- Categoria x Responsável: crosstab mostra volume de cada categoria por atendente
- Categoria x Urgência: quais categorias são tratadas como mais urgentes
"""

import pandas as pd

df = pd.read_csv("output/tickets_limpos.csv", parse_dates=["Aberto em"])

print("=" * 60)
print("PARETO DE CLIENTES (ORGANIZAÇÃO)")
print("=" * 60)
volume_cliente = df["Organização"].value_counts()
acumulado_pct = (volume_cliente.cumsum() / volume_cliente.sum() * 100).round(1)

n_clientes = len(volume_cliente)
n_80pct = (acumulado_pct <= 80).sum()
print(f"Total de organizações distintas: {n_clientes}")
print(f"Organizações que somam 80% do volume: {n_80pct} ({n_80pct/n_clientes*100:.1f}% das organizações)")
print("\nTop 15 organizações por volume:")
top15 = pd.DataFrame({"qtd_tickets": volume_cliente.head(15), "% acumulado": acumulado_pct.head(15)})
print(top15)

print("\n" + "=" * 60)
print("CATEGORIA x RESPONSÁVEL (top 7 responsáveis)")
print("=" * 60)
top_responsaveis = df["Responsável"].value_counts().head(7).index
crosstab = pd.crosstab(df["Categoria"], df["Responsável"])[top_responsaveis]
print(crosstab)

print("\n" + "=" * 60)
print("CATEGORIA x URGÊNCIA (%)")
print("=" * 60)
crosstab_urg = pd.crosstab(df["Categoria"], df["Urgência"], normalize="index").mul(100).round(1)
print(crosstab_urg)

# Salva para uso posterior (gráficos / Power BI)
top15.to_csv("output/pareto_clientes.csv")
crosstab.to_csv("output/categoria_x_responsavel.csv")
crosstab_urg.to_csv("output/categoria_x_urgencia.csv")
print("\nAgregados salvos em output/")
