"""
Aula 2 - Limpeza e padronização.

O que fazemos aqui:
1. Descartar colunas sem valor analítico (constantes ou quase todas vazias)
2. Separar "Organização » Contato" em duas colunas
3. Corrigir "Cliente: Classificação" que vem duplicada (ex: "Empresa,Empresa")
4. Derivar colunas de tempo a partir de "Aberto em" (dia da semana, mês, semana)

O resultado é salvo em output/tickets_limpos.csv, que vai virar a base
de todas as próximas aulas (e também poderá alimentar o Power BI depois).
"""

import pandas as pd

df = pd.read_excel("data/TicketSuporteCem.xlsx")

# 1) Descarta colunas sem informação útil
#    - Serviço (2º Nível): valor único em todas as linhas
#    - Justificativa: 99.8% vazia
df = df.drop(columns=["Serviço (2º Nível)", "Justificativa"])

# 2) Separa "Organização » Contato".
#    expand=True devolve um DataFrame com uma coluna por pedaço do split;
#    n=1 garante que só quebramos na primeira ocorrência de " » ".
partes = df["Cliente (Completo)"].str.split(" » ", n=1, expand=True)
df["Organização"] = partes[0].str.strip()
df["Contato"] = partes[1].str.strip() if 1 in partes.columns else pd.NA

# 3) Corrige classificação duplicada tipo "Empresa,Empresa" -> "Empresa"
def limpar_classificacao(valor):
    if pd.isna(valor):
        return valor
    partes_unicas = dict.fromkeys(p.strip() for p in valor.split(","))
    return ", ".join(partes_unicas)

df["Classificação Cliente"] = df["Cliente: Classificação (Organização)"].apply(limpar_classificacao)
df = df.drop(columns=["Cliente: Classificação (Organização)", "Cliente (Completo)"])
df["Classificação Cliente"] = df["Classificação Cliente"].fillna("Não classificado")

# 4) Colunas derivadas de data (o acessor .dt dá acesso a partes da data)
df["Dia da Semana"] = df["Aberto em"].dt.day_name()
df["Ano-Mês"] = df["Aberto em"].dt.to_period("M").astype(str)
df["Semana"] = df["Aberto em"].dt.isocalendar().week

# Traduz dias da semana para português (dt.day_name() vem em inglês)
DIAS_PT = {
    "Monday": "Segunda", "Tuesday": "Terça", "Wednesday": "Quarta",
    "Thursday": "Quinta", "Friday": "Sexta", "Saturday": "Sábado", "Sunday": "Domingo",
}
df["Dia da Semana"] = df["Dia da Semana"].map(DIAS_PT)

print("=" * 60)
print("RESULTADO DA LIMPEZA")
print("=" * 60)
print(f"Colunas finais: {list(df.columns)}")
print(f"Linhas: {len(df)}")
print()
print(df[["Organização", "Contato", "Classificação Cliente", "Dia da Semana", "Ano-Mês"]].head())

df.to_csv("output/tickets_limpos.csv", index=False, encoding="utf-8-sig")
print("\nSalvo em output/tickets_limpos.csv")
