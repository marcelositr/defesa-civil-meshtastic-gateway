#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from defesa_civil_localizacao import (
    alerta_atinge_localizacao,
    buscar_alertas,
    ler_poligono,
    ponto_no_poligono,
)


# ============================================================
# LOCALIZAÇÃO DE TESTE
# ============================================================

LOCATION_NAME = "Ituverava"
LOCATION_LAT = -20.339
LOCATION_LON = -47.780


# ============================================================
# TESTE POINT IN POLYGON
# ============================================================

POLYGON_TEXT = """
-22.500,-45.800
-22.500,-45.400
-23.000,-45.400
-23.000,-45.800
-22.500,-45.800
"""

polygon = ler_poligono(POLYGON_TEXT)

assert len(polygon) == 5
assert ponto_no_poligono(
    -22.739,
    -45.591,
    polygon,
)

assert not ponto_no_poligono(
    LOCATION_LAT,
    LOCATION_LON,
    polygon,
)

print("=" * 80)
print("DEFESA CIVIL - TESTE DE LOCALIZAÇÃO")
print("=" * 80)

print()
print(f"Local: {LOCATION_NAME}")
print(f"Latitude:  {LOCATION_LAT}")
print(f"Longitude: {LOCATION_LON}")
print()

print("Teste geométrico: OK")


# ============================================================
# TESTE DO FEED OFICIAL
# ============================================================

print()
print("Consultando feed oficial da Defesa Civil...")

entries = buscar_alertas()

print(
    f"Alertas recebidos: {len(entries)}"
)

print()

# ============================================================
# TESTAR CADA ALERTA
# ============================================================

alertas_encontrados = 0

for entry in entries:

    alerta = alerta_atinge_localizacao(
        entry,
        LOCATION_LAT,
        LOCATION_LON,
    )

    if alerta is None:
        continue

    alertas_encontrados += 1

    print("=" * 80)
    print("ALERTA ATINGE A LOCALIZAÇÃO")
    print("=" * 80)

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
    print("Headline:")
    print(alerta["headline"])
    print()


# ============================================================
# RESULTADO
# ============================================================

print("=" * 80)
print("RESULTADO")
print("=" * 80)

print(
    f"Local testado:       {LOCATION_NAME}"
)

print(
    f"Alertas encontrados: {alertas_encontrados}"
)

print()
print("Teste de localização concluído com o código do projeto.")
