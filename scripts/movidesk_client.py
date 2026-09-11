"""
Cliente HTTP simples para a API pública do Movidesk.

Referências oficiais:
- API de Tickets:  https://atendimento.movidesk.com/kb/article/256/movidesk-ticket-api
- API de Pessoas:  https://atendimento.movidesk.com/kb/pt-br/article/189/movidesk-person-api
- Limites de uso:  https://atendimento.movidesk.com/kb/article/272370/horario-e-limite-de-acesso-da-api

O token é lido da variável de ambiente MOVIDESK_TOKEN (veja .env.example).

Como gerar o token no Movidesk:
  Configurações (engrenagem) > Conta > Parâmetros > aba "Ambiente" >
  role até "API" > botão "Gerar nova chave" (se ainda não existir uma).
  Atenção: gerar uma chave nova invalida a anterior em todos os lugares
  que a utilizam.
"""

import os
import time
import requests

BASE_URL = "https://api.movidesk.com/public/v1"

# A Movidesk libera no máximo 10 requisições/minuto por IP. Usamos um
# intervalo um pouco acima de 6s entre chamadas (10 req / 65s) como margem
# de segurança para não sofrer bloqueio 429.
INTERVALO_MINIMO_ENTRE_REQUISICOES = 6.5  # segundos

_ultimo_request = 0.0


def _respeitar_limite_de_taxa():
    global _ultimo_request
    agora = time.monotonic()
    espera = INTERVALO_MINIMO_ENTRE_REQUISICOES - (agora - _ultimo_request)
    if espera > 0:
        time.sleep(espera)
    _ultimo_request = time.monotonic()


def _token():
    token = os.environ.get("MOVIDESK_TOKEN")
    if not token:
        raise RuntimeError(
            "Variável de ambiente MOVIDESK_TOKEN não encontrada.\n"
            "Copie .env.example para .env e cole o token da API do Movidesk "
            "(Configurações > Conta > Parâmetros > aba Ambiente > Gerar nova chave)."
        )
    return token


def _get(path, params):
    params = dict(params)
    params["token"] = _token()

    tentativas_com_erro = 0
    while True:
        _respeitar_limite_de_taxa()
        resposta = requests.get(f"{BASE_URL}{path}", params=params, timeout=60)

        if resposta.status_code == 200:
            return resposta.json()

        if resposta.status_code == 429:
            # A API manda quanto tempo falta pra liberar de novo no header
            # 'retry-after'. Se não vier, usamos um valor conservador.
            espera = int(resposta.headers.get("retry-after", 60))
            print(f"    ... limite de requisições atingido, aguardando {espera}s")
            time.sleep(espera + 1)
            tentativas_com_erro += 1
            if tentativas_com_erro > 5:
                resposta.raise_for_status()
            continue

        # Outros erros (401 token inválido, 400 filtro malformado etc.)
        # -> mostra o corpo da resposta, que costuma trazer o motivo exato.
        try:
            detalhe = resposta.json()
        except ValueError:
            detalhe = resposta.text
        print(f"    Erro {resposta.status_code} em {path}: {detalhe}")
        resposta.raise_for_status()


def _paginar(path, select, filtro=None, expand=None, tamanho_pagina=300):
    """Segue $skip até a página voltar menor que o tamanho pedido."""
    itens = []
    skip = 0
    while True:
        params = {"$select": select, "$top": tamanho_pagina, "$skip": skip}
        if filtro:
            params["$filter"] = filtro
        if expand:
            params["$expand"] = expand

        pagina = _get(path, params)
        itens.extend(pagina)
        print(f"  ... {path} — {len(itens)} registros carregados até agora")

        if len(pagina) < tamanho_pagina:
            break
        skip += tamanho_pagina

    return itens


def buscar_tickets(data_inicio, data_fim):
    """
    Busca tickets com createdDate entre data_inicio e data_fim (datetimes,
    interpretados como UTC).

    Atenção: a rota /tickets só retorna tickets com lastUpdate < 90 dias.
    Tickets mais antigos (parados/fechados há mais tempo) exigem a rota
    /tickets/past: https://atendimento.movidesk.com/kb/article/446011
    """
    filtro = (
        f"createdDate ge {data_inicio.strftime('%Y-%m-%dT%H:%M:%S')}.00z "
        f"and createdDate le {data_fim.strftime('%Y-%m-%dT%H:%M:%S')}.00z"
    )
    select = (
        "id,type,subject,createdDate,category,urgency,status,justification,"
        "ownerTeam,serviceFull,serviceSecondLevel"
    )
    # owner e clients são objetos/listas aninhadas: precisam de $expand para
    # virem preenchidos (o $select sozinho só resolve campos escalares).
    expand = "owner,clients($expand=organization)"
    return _paginar("/tickets", select=select, filtro=filtro, expand=expand)


def buscar_classificacao_organizacoes():
    """
    Retorna um dicionário {id_organizacao: classificacao} para todas as
    organizações (personType=2, Empresa) cadastradas na base. Usado para
    preencher "Cliente: Classificação (Organização)", que a API de Tickets
    não devolve dentro do objeto organization aninhado.
    """
    itens = _paginar(
        "/persons",
        select="id,businessName,classification",
        filtro="personType eq 2",
        tamanho_pagina=500,
    )
    return {p["id"]: p.get("classification") for p in itens}
