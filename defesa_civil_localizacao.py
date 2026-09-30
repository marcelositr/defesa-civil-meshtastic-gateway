#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET

from config import (
    DEFESA_CIVIL_URL,
    GATEWAY_NAME,
    LATITUDE,
    LOCATION_MODE,
    LONGITUDE,
)


# ============================================================
# NAMESPACES
# ============================================================

ATOM_NS = "http://www.w3.org/2005/Atom"
CAP_NS = "urn:oasis:names:tc:emergency:cap:1.2"

NS = {
    "atom": ATOM_NS,
    "cap": CAP_NS,
}


# ============================================================
# LOCALIZAÇÃO
# ============================================================

def obter_localizacao_manual():
    """
    Retorna a localização configurada manualmente.

    A localização manual é útil quando:

    - o GPS está desativado;
    - o equipamento não possui GPS;
    - o usuário não deseja utilizar sua posição real;
    - o usuário deseja representar uma área aproximada;
    - o equipamento está instalado em uma posição fixa.

    Retorna:

        nome, latitude, longitude
    """

    return (
        GATEWAY_NAME,
        LATITUDE,
        LONGITUDE,
    )


def obter_localizacao_gps():
    """
    Obtém a localização atual através do GPS do nó Meshtastic.

    ESTA FUNÇÃO AINDA NÃO ESTÁ IMPLEMENTADA.

    Quando o Heltec estiver disponível, esta função será
    responsável por consultar a interface Meshtastic e obter
    a posição GPS do nó.

    O retorno esperado será:

        nome, latitude, longitude

    O nome continuará sendo uma configuração independente
    das coordenadas.

    IMPORTANTE:

    A posição GPS será utilizada apenas localmente para
    verificar se o ponto está dentro do polígono de um alerta.

    A aplicação não deve publicar a latitude ou longitude
    simplesmente por utilizar o GPS.

    Retorna:

        nome, latitude, longitude
    """

    raise NotImplementedError(
        "Localização GPS ainda não implementada."
    )


def obter_localizacao():
    """
    Seleciona a fonte da localização de acordo com
    LOCATION_MODE.

    Modos disponíveis:

        manual
        gps

    No modo manual, as coordenadas configuradas pelo usuário
    são utilizadas.

    No modo GPS, a posição será obtida do nó Meshtastic.
    """

    if LOCATION_MODE == "manual":

        return obter_localizacao_manual()

    if LOCATION_MODE == "gps":

        return obter_localizacao_gps()

    raise ValueError(
        f"LOCATION_MODE inválido: {LOCATION_MODE}"
    )


# ============================================================
# POINT IN POLYGON
# ============================================================

def ponto_no_poligono(lat, lon, polygon):

    dentro = False

    j = len(polygon) - 1

    for i in range(len(polygon)):

        lat_i, lon_i = polygon[i]
        lat_j, lon_j = polygon[j]

        if ((lon_i > lon) != (lon_j > lon)):

            intersecao = (
                (lat_j - lat_i)
                * (lon - lon_i)
                / (lon_j - lon_i)
                + lat_i
            )

            if lat < intersecao:
                dentro = not dentro

        j = i

    return dentro


# ============================================================
# PARSE POLYGON
# ============================================================

def ler_poligono(texto):

    pontos = []

    for par in texto.split():

        try:

            lat, lon = map(
                float,
                par.split(",")
            )

            pontos.append(
                (lat, lon)
            )

        except ValueError:
            continue

    return pontos


# ============================================================
# BUSCAR ALERTAS
# ============================================================

def buscar_alertas():

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": (
            "application/rss+xml, "
            "application/xml, "
            "text/xml"
        ),
    }

    response = requests.get(
        DEFESA_CIVIL_URL,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    root = ET.fromstring(
        response.content
    )

    return root.findall(
        "atom:entry",
        NS,
    )


# ============================================================
# VERIFICAR ALERTA
# ============================================================

def alerta_atinge_localizacao(
    entry,
    latitude,
    longitude,
):

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

                return {
                    "id": alert.findtext(
                        "cap:identifier",
                        "",
                        NS,
                    ),
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
                    "sender": info.findtext(
                        "cap:senderName",
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
                }

    return None


# ============================================================
# VERIFICAR ALERTA PROCESSADO
# ============================================================

def alerta_processado_atinge_localizacao(
    alerta,
    latitude,
    longitude,
):
    """
    Verifica se um alerta CAP já processado atinge a localização.

    A função recebe o dicionário produzido por
    defesa_civil_alertas.extrair_alerta() e retorna True quando
    a localização está dentro de pelo menos um polígono.
    """

    info = alerta.get("info")

    if info is None:
        return False

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
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("DEFESA CIVIL - MOTOR DE LOCALIZAÇÃO")
    print("=" * 80)

    print()

    nome, latitude, longitude = (
        obter_localizacao()
    )

    print(f"Modo:       {LOCATION_MODE}")
    print(f"Local:      {nome}")
    print(f"Latitude:   {latitude}")
    print(f"Longitude:  {longitude}")
    print()

    print("Consultando Defesa Civil...")

    entries = buscar_alertas()

    print(
        f"Alertas recebidos: {len(entries)}"
    )

    print()

    encontrados = []

    for entry in entries:

        alerta = alerta_atinge_localizacao(
            entry,
            latitude,
            longitude,
        )

        if alerta is not None:
            encontrados.append(
                alerta
            )

    # ========================================================
    # RESULTADO
    # ========================================================

    print("=" * 80)
    print("RESULTADO")
    print("=" * 80)

    print(
        f"Local: {nome}"
    )

    print(
        f"Alertas que atingem a localização: "
        f"{len(encontrados)}"
    )

    print()

    for alerta in encontrados:

        print("-" * 80)

        print(
            f"ID:         {alerta['id']}"
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

        print(
            "Headline:"
        )

        print(
            alerta["headline"]
        )

        print()


if __name__ == "__main__":
    main()