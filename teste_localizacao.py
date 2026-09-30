#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET


URL = "https://idapfile.mdr.gov.br/idap/api/rss/cap"

# ============================================================
# LOCALIZAÇÃO DE TESTE
# ============================================================

LOCATION_NAME = "Ituverava"
LOCATION_LAT = -20.339
LOCATION_LON = -47.780


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
# POINT IN POLYGON
# ============================================================

def ponto_no_poligono(lat, lon, polygon):
    """
    Verifica se um ponto está dentro de um polígono.

    polygon:
        lista de (latitude, longitude)
    """

    dentro = False

    j = len(polygon) - 1

    for i in range(len(polygon)):

        lat_i, lon_i = polygon[i]
        lat_j, lon_j = polygon[j]

        if ((lon_i > lon) != (lon_j > lon)):
            intersecao = (
                lat_j - lat_i
            ) * (
                lon - lon_i
            ) / (
                lon_j - lon_i
            ) + lat_i

            if lat < intersecao:
                dentro = not dentro

        j = i

    return dentro


# ============================================================
# PARSE POLYGON
# ============================================================

def ler_poligono(texto):
    """
    Converte:

        lat,lon lat,lon lat,lon ...

    em:

        [(lat, lon), ...]
    """

    pontos = []

    for par in texto.split():

        try:
            lat, lon = map(float, par.split(","))
            pontos.append((lat, lon))
        except ValueError:
            continue

    return pontos


# ============================================================
# BUSCAR ALERTAS
# ============================================================

print("=" * 80)
print("DEFESA CIVIL - TESTE DE LOCALIZAÇÃO")
print("=" * 80)

print()
print(f"Local: {LOCATION_NAME}")
print(f"Latitude:  {LOCATION_LAT}")
print(f"Longitude: {LOCATION_LON}")
print()

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/rss+xml, application/xml, text/xml",
}

response = requests.get(
    URL,
    headers=headers,
    timeout=30,
)

print(f"HTTP: {response.status_code}")
print()

response.raise_for_status()

root = ET.fromstring(response.content)

entries = root.findall("atom:entry", NS)

print(f"Alertas recebidos: {len(entries)}")
print()

# ============================================================
# TESTAR CADA ALERTA
# ============================================================

alertas_encontrados = 0
alertas_testados = 0

for entry in entries:

    content = entry.find("atom:content", NS)

    if content is None:
        continue

    alert = content.find("cap:alert", NS)

    if alert is None:
        continue

    identifier = alert.findtext(
        "cap:identifier",
        default="",
        namespaces=NS,
    )

    info = alert.find("cap:info", NS)

    if info is None:
        continue

    event = info.findtext(
        "cap:event",
        default="",
        namespaces=NS,
    )

    urgency = info.findtext(
        "cap:urgency",
        default="",
        namespaces=NS,
    )

    severity = info.findtext(
        "cap:severity",
        default="",
        namespaces=NS,
    )

    certainty = info.findtext(
        "cap:certainty",
        default="",
        namespaces=NS,
    )

    sender_name = info.findtext(
        "cap:senderName",
        default="",
        namespaces=NS,
    )

    headline = info.findtext(
        "cap:headline",
        default="",
        namespaces=NS,
    )

    areas = info.findall("cap:area", NS)

    encontrou = False

    for area in areas:

        polygons = area.findall("cap:polygon", NS)

        for polygon_element in polygons:

            polygon_text = polygon_element.text

            if not polygon_text:
                continue

            polygon = ler_poligono(polygon_text)

            if len(polygon) < 3:
                continue

            alertas_testados += 1

            if ponto_no_poligono(
                LOCATION_LAT,
                LOCATION_LON,
                polygon,
            ):
                encontrou = True
                break

        if encontrou:
            break

    if encontrou:

        alertas_encontrados += 1

        print("=" * 80)
        print("⚠️ ALERTA ATINGE A LOCALIZAÇÃO")
        print("=" * 80)

        print(f"ID:         {identifier}")
        print(f"Evento:     {event}")
        print(f"Urgência:   {urgency}")
        print(f"Severidade: {severity}")
        print(f"Certeza:    {certainty}")
        print(f"Emissor:    {sender_name}")
        print()
        print(f"Headline:")
        print(headline)
        print()


# ============================================================
# RESULTADO
# ============================================================

print("=" * 80)
print("RESULTADO")
print("=" * 80)

print(f"Local testado:       {LOCATION_NAME}")
print(f"Coordenadas:         {LOCATION_LAT}, {LOCATION_LON}")
print(f"Polígonos testados:  {alertas_testados}")
print(f"Alertas encontrados: {alertas_encontrados}")
print()

if alertas_encontrados:
    print("⚠️ Existem alertas cujo polígono contém o ponto.")
else:
    print("✓ Nenhum alerta contém o ponto.")