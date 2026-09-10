"""
Aula 1 - Carga e primeira exploração dos dados de tickets de suporte.

Objetivo: ler o Excel e responder as perguntas básicas
- quantas linhas/colunas?
- quais tipos de dado em cada coluna?
- quantos valores nulos (faltantes)?
- qual o período coberto?
"""

import pandas as pd

CAMINHO_ARQUIVO = "data/TicketSuporteCem.xlsx"

# read_excel devolve um DataFrame: uma tabela com linhas e colunas, indexada por posição
df = pd.read_excel(CAMINHO_ARQUIVO)

print("=" * 60)
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
