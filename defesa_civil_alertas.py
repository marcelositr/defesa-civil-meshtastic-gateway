#!/usr/bin/env python3

import datetime
import hashlib
import json
import os
import requests
import xml.etree.ElementTree as ET

from config import (
    GATEWAY_NAME,
    LATITUDE,
    LOCATION_MODE,
    LONGITUDE,
    MAX_MESSAGE_LENGTH,
    STATE_FILE,
)
from defesa_civil_localizacao import (
    alerta_atinge_localizacao,
    buscar_alertas,
    obter_localizacao,
)


# ============================================================
# EXTRAIR ALERTA
# ============================================================

def extrair_alerta(entry):

    content = entry.find(
        "atom:content",
        NS,
    )

    if content is None:
        return None

    alert = content.find(
        "cap:alert",
        NS,
    )

    if alert is None:
        return None

    info = alert.find(
        "cap:info",
        NS,
    )

    if info is None:
        return None

    references = []

    for elemento in alert.findall(
        "cap:references",
        NS,
    ):

        if elemento.text:
            references.append(
                elemento.text
            )

    return {
        "id": alert.findtext(
            "cap:identifier",
            "",
            NS,
        ),
        "sender": alert.findtext(
            "cap:sender",
            "",
            NS,
        ),
        "sent": alert.findtext(
            "cap:sent",
            "",
            NS,
        ),
        "status": alert.findtext(
            "cap:status",
            "",
            NS,
        ),
        "msgType": alert.findtext(
            "cap:msgType",
            "",
            NS,
        ),
        "references": references,
        "event": info.findtext(
            "cap:event",
            "",
            NS,
        ),
        "urgency": info.findtext(
            "cap:urgency",
            "",
            NS,
        ),
        "severity": info.findtext(
            "cap:severity",
            "",
            NS,
        ),
        "certainty": info.findtext(
            "cap:certainty",
            "",
            NS,
        ),
        "onset": info.findtext(
            "cap:onset",
            "",
            NS,
        ),
        "expires": info.findtext(
            "cap:expires",
            "",
            NS,
        ),
        "headline": info.findtext(
            "cap:headline",
            "",
            NS,
        ),
        "description": info.findtext(
            "cap:description",
            "",
            NS,
        ),
        "instruction": info.findtext(
            "cap:instruction",
            "",
            NS,
        ),
        "senderName": info.findtext(
            "cap:senderName",
            "",
            NS,
        ),
        "info": info,
    }


# ============================================================
# VERIFICAR LOCALIZAÇÃO
# ============================================================

def alerta_atinge_localizacao(
    alerta,
    latitude,
    longitude,
):

    info = alerta["info"]

    areas = info.findall(
        "cap:area",
        NS,
    )

    for area in areas:

        polygons = area.findall(
            "cap:polygon",
            NS,
        )

        for polygon_element in polygons:

            if not polygon_element.text:
                continue

            polygon = ler_poligono(
                polygon_element.text
            )

            if len(polygon) < 3:
                continue

            if ponto_no_poligono(
                latitude,
                longitude,
                polygon,
            ):
                return True

    return False


# ============================================================
# EXPIRAÇÃO
# ============================================================

def alerta_expirado(alerta):

    expires = alerta.get(
        "expires",
        "",
    )

    if not expires:
        return False

    try:

        data_expiracao = (
            datetime.datetime.fromisoformat(
                expires
            )
        )

    except ValueError:
        return False

    agora = datetime.datetime.now(
        datetime.timezone.utc
    )

    if data_expiracao.tzinfo is None:
        data_expiracao = data_expiracao.replace(
            tzinfo=datetime.timezone.utc
        )

    return data_expiracao <= agora


# ============================================================
# REFERÊNCIAS
# ============================================================

def obter_ids_referenciados(alerta):

    ids = []

    for referencia in alerta.get(
        "references",
        [],
    ):

        for grupo in referencia.split():

            partes = grupo.split(",")

            if partes:
                identifier = partes[0].strip()

                if identifier:
                    ids.append(identifier)

    return ids


# ============================================================
# ASSINATURA DO ALERTA
# ============================================================

def criar_assinatura(alerta):

    """
    Cria uma assinatura do conteúdo relevante do alerta.

    O identifier sozinho identifica o alerta, mas não permite
    detectar uma atualização do mesmo alerta.

    Por isso utilizamos também os principais campos do CAP.

    Se qualquer um deles mudar, a assinatura muda.
    """

    dados = [
        alerta.get("id", ""),
        alerta.get("sender", ""),
        alerta.get("sent", ""),
        alerta.get("status", ""),
        alerta.get("msgType", ""),
        alerta.get("event", ""),
        alerta.get("urgency", ""),
        alerta.get("severity", ""),
        alerta.get("certainty", ""),
        alerta.get("onset", ""),
        alerta.get("expires", ""),
        alerta.get("headline", ""),
        alerta.get("description", ""),
        alerta.get("instruction", ""),
        "|".join(
            alerta.get(
                "references",
                [],
            )
        ),
    ]

    texto = "|".join(dados)

    return hashlib.sha256(
        texto.encode("utf-8")
    ).hexdigest()


# ============================================================
# ESTADO
# ============================================================

def carregar_estado():

    if not os.path.exists(STATE_FILE):
        return {}

    try:

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8",
        ) as arquivo:

            return json.load(arquivo)

    except (
        json.JSONDecodeError,
        OSError,
    ):

        return {}


def salvar_estado(estado):

    arquivo_temporario = (
        STATE_FILE + ".tmp"
    )

    with open(
        arquivo_temporario,
        "w",
        encoding="utf-8",
    ) as arquivo:

        json.dump(
            estado,
            arquivo,
            indent=2,
            ensure_ascii=False,
        )

    os.replace(
        arquivo_temporario,
        STATE_FILE,
    )


def alerta_para_estado(alerta, assinatura):

    return {
        "signature": assinatura,
        "status": alerta.get(
            "status",
            "",
        ),
        "msgType": alerta.get(
            "msgType",
            "",
        ),
        "sent": alerta.get(
            "sent",
            "",
        ),
        "expires": alerta.get(
            "expires",
            "",
        ),
        "active": True,
    }


# ============================================================
# PROCESSAR ALERTAS
# ============================================================

def processar_alertas(
    entries,
    latitude,
    longitude,
):

    estado = carregar_estado()

    novos = []
    atualizados = []
    ignorados = []

    for entry in entries:

        alerta = extrair_alerta(entry)

        if alerta is None:
            continue

        status = alerta.get(
            "status",
            "",
        )

        msg_type = alerta.get(
            "msgType",
            "",
        )

        if status != "Actual":
            continue

        referencias = obter_ids_referenciados(
            alerta
        )

        # ====================================================
        # CANCEL
        # ====================================================

        if msg_type == "Cancel":

            for identifier in referencias:

                anterior = estado.get(
                    identifier
                )

                if anterior is not None:

                    anterior["active"] = False

            continue

        # ====================================================
        # UPDATE
        # ====================================================

        if msg_type == "Update":

            if not alerta_atinge_localizacao(
                alerta,
                latitude,
                longitude,
            ):
                continue

            assinatura = criar_assinatura(
                alerta
            )

            alvo = None

            for identifier in referencias:

                if identifier in estado:
                    alvo = identifier
                    break

            if alvo is not None:

                anterior = estado.get(
                    alvo
                )

                if (
                    anterior is not None
                    and anterior.get("signature")
                    != assinatura
                ):

                    atualizados.append(
                        alerta
                    )

                    anterior["active"] = False

                    estado[alerta["id"]] = (
                        alerta_para_estado(
                            alerta,
                            assinatura,
                        )
                    )

                else:

                    ignorados.append(
                        alerta
                    )

            else:

                if alerta_expirado(alerta):
                    continue

                novos.append(
                    alerta
                )

                estado[alerta["id"]] = (
                    alerta_para_estado(
                        alerta,
                        assinatura,
                    )
                )

            continue

        # ====================================================
        # ALERT
        # ====================================================

        if msg_type != "Alert":
            continue

        if alerta_expirado(alerta):
            continue

        if not alerta_atinge_localizacao(
            alerta,
            latitude,
            longitude,
        ):
            continue

        identifier = alerta["id"]

        assinatura = criar_assinatura(
            alerta
        )

        anterior = estado.get(
            identifier
        )

        if anterior is None:

            novos.append(
                alerta
            )

            estado[identifier] = (
                alerta_para_estado(
                    alerta,
                    assinatura,
                )
            )

        elif (
            anterior.get("active", True)
            and anterior.get("signature")
            != assinatura
        ):

            atualizados.append(
                alerta
            )

            estado[identifier] = (
                alerta_para_estado(
                    alerta,
                    assinatura,
                )
            )

        else:

            ignorados.append(
                alerta
            )

    salvar_estado(estado)

    return (
        novos,
        atualizados,
        ignorados,
    )


# ============================================================
# MENSAGEM OFICIAL
# ============================================================

def montar_texto_oficial(alerta):

    """
    Monta o conteúdo que será retransmitido.

    O headline é a nota principal publicada pela Defesa Civil.

    A description não é utilizada porque, conforme observado
    no feed real, ela frequentemente duplica o headline.

    A instruction é uma orientação oficial adicional e é
    preservada integralmente.

    Nenhum dos textos é resumido, reescrito ou truncado.
    """

    headline = alerta.get(
        "headline",
        "",
    )

    instruction = alerta.get(
        "instruction",
        "",
    )

    partes = []

    if headline:
        partes.append(
            headline
        )

    if instruction:
        partes.append(
            instruction
        )

    return "\n\n".join(
        partes
    )


# ============================================================
# DIVIDIR MENSAGEM
# ============================================================

def dividir_mensagem(
    texto,
    max_length,
):

    if not texto:
        return []

    if len(texto) <= max_length:
        return [texto]

    partes = []

    inicio = 0
    tamanho = len(texto)

    while inicio < tamanho:

        limite = min(
            inicio + max_length,
            tamanho,
        )

        if limite >= tamanho:

            partes.append(
                texto[inicio:limite]
            )

            break

        corte = texto.rfind(
            " ",
            inicio,
            limite + 1,
        )

        if corte <= inicio:

            corte = limite

        else:

            # O espaço utilizado como ponto de divisão
            # permanece no texto para não perder conteúdo.
            corte += 1

        partes.append(
            texto[inicio:corte]
        )

        inicio = corte

    return partes


# ============================================================
# MONTAR MENSAGENS MESHTASTIC
# ============================================================

def montar_mensagens(alerta):

    texto = montar_texto_oficial(
        alerta
    )

    if not texto:
        return []

    # Primeiro fazemos uma divisão preliminar.
    #
    # O número final de partes precisa ser conhecido antes
    # de inserir o marcador [DEFESA CIVIL X/N].

    partes = dividir_mensagem(
        texto,
        MAX_MESSAGE_LENGTH,
    )

    total = len(partes)

    mensagens = []

    while True:

        novas = []

        for indice, parte in enumerate(
            partes,
            start=1,
        ):

            marcador = (
                f"[DEFESA CIVIL {indice}/{total}]\n"
            )

            espaco_disponivel = (
                MAX_MESSAGE_LENGTH
                - len(marcador)
            )

            if espaco_disponivel <= 0:
                raise ValueError(
                    "MAX_MESSAGE_LENGTH é muito pequeno "
                    "para o marcador da mensagem."
                )

            if len(parte) > espaco_disponivel:

                novas = dividir_mensagem(
                    texto,
                    espaco_disponivel,
                )

                break

        if not novas:
            mensagens = [
                (
                    f"[DEFESA CIVIL {indice}/{total}]\n"
                    f"{parte}"
                )
                for indice, parte in enumerate(
                    partes,
                    start=1,
                )
            ]

            break

        partes = novas
        total = len(partes)

    return mensagens


# ============================================================
# EXIBIR ALERTA
# ============================================================

def exibir_alerta(
    titulo,
    alerta,
):

    print("-" * 80)

    print(titulo)

    print(
        f"ID:         {alerta['id']}"
    )

    print(
        f"Tipo:       {alerta['msgType']}"
    )

    print(
        f"Evento:     {alerta['event']}"
    )

    print(
        f"Urgência:   {alerta['urgency']}"
    )

    print(
        f"Severidade: {alerta['severity']}"
    )

    print(
        f"Certeza:    {alerta['certainty']}"
    )

    print(
        f"Emissor:    {alerta['sender']}"
    )

    print()

    print("Mensagem Meshtastic:")

    print()

    mensagens = montar_mensagens(
        alerta
    )

    for mensagem in mensagens:

        print(mensagem)
        print()


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("DEFESA CIVIL - PROCESSADOR DE ALERTAS")
    print("=" * 80)

    print()

    nome, latitude, longitude = (
        obter_localizacao()
    )

    print(
        f"Modo:       {LOCATION_MODE}"
    )

    print(
        f"Local:      {nome}"
    )

    print(
        f"Latitude:   {latitude}"
    )

    print(
        f"Longitude:  {longitude}"
    )

    print()

    print(
        "Consultando feed oficial da Defesa Civil..."
    )

    entries = buscar_alertas()

    print(
        f"Alertas recebidos: {len(entries)}"
    )

    print()

    novos, atualizados, ignorados = (
        processar_alertas(
            entries,
            latitude,
            longitude,
        )
    )

    print("=" * 80)
    print("RESULTADO")
    print("=" * 80)

    print(
        f"Novos:        {len(novos)}"
    )

    print(
        f"Atualizados:  {len(atualizados)}"
    )

    print(
        f"Ignorados:    {len(ignorados)}"
    )

    print()

    for alerta in novos:

        exibir_alerta(
            "NOVO ALERTA",
            alerta,
        )

    for alerta in atualizados:

        exibir_alerta(
            "ALERTA ATUALIZADO",
            alerta,
        )

    if not novos and not atualizados:

        print(
            "Nenhum alerta novo ou atualizado "
            "atinge a localização."
        )


if __name__ == "__main__":
    main()