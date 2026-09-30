#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET


URL = "https://idapfile.mdr.gov.br/idap/api/rss/cap"

ATOM_NS = "http://www.w3.org/2005/Atom"
CAP_NS = "urn:oasis:names:tc:emergency:cap:1.2"

NS = {
    "atom": ATOM_NS,
    "cap": CAP_NS,
}


def buscar_feed():
    print("Baixando alertas da Defesa Civil...")

    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    return ET.fromstring(response.content)


def extrair_alertas(root):

    alertas = []

    entries = root.findall("atom:entry", NS)

    print("Entradas encontradas:", len(entries))

    for entry in entries:

        content = entry.find("atom:content", NS)

        if content is None:
            continue

        # O <alert> está dentro do <content>
        alert = content.find("cap:alert", NS)

        if alert is None:
            continue

        info = alert.find("cap:info", NS)

        if info is None:
            continue

        dados = {
            "id": alert.findtext("cap:identifier", "", NS),
            "sender": alert.findtext("cap:sender", "", NS),
            "sent": alert.findtext("cap:sent", "", NS),
            "status": alert.findtext("cap:status", "", NS),
            "msg_type": alert.findtext("cap:msgType", "", NS),
            "event": info.findtext("cap:event", "", NS),
            "urgency": info.findtext("cap:urgency", "", NS),
            "severity": info.findtext("cap:severity", "", NS),
            "certainty": info.findtext("cap:certainty", "", NS),
            "onset": info.findtext("cap:onset", "", NS),
            "expires": info.findtext("cap:expires", "", NS),
            "sender_name": info.findtext("cap:senderName", "", NS),
            "headline": info.findtext("cap:headline", "", NS),
            "description": info.findtext("cap:description", "", NS),
            "instruction": info.findtext("cap:instruction", "", NS),
            "areas": [],
        }

        # Áreas afetadas
        for area in info.findall("cap:area", NS):

            area_data = {
                "description": area.findtext(
                    "cap:areaDesc", "", NS
                ),
                "polygons": [],
            }

            for polygon in area.findall("cap:polygon", NS):
                if polygon.text:
                    area_data["polygons"].append(
                        polygon.text.strip()
                    )

            dados["areas"].append(area_data)

        alertas.append(dados)

    return alertas


def mostrar_alertas(alertas):

    print()
    print("=" * 70)
    print("ALERTAS ENCONTRADOS:", len(alertas))
    print("=" * 70)

    for numero, alerta in enumerate(alertas, start=1):

        print()
        print(f"[{numero}]")
        print("-" * 70)

        print("ID:", alerta["id"])
        print("Remetente:", alerta["sender"])
        print("Status:", alerta["status"])
        print("Tipo:", alerta["msg_type"])

        print()
        print("Evento:", alerta["event"])
        print("Urgência:", alerta["urgency"])
        print("Severidade:", alerta["severity"])
        print("Certeza:", alerta["certainty"])

        print()
        print("Início:", alerta["onset"])
        print("Expira:", alerta["expires"])

        print()
        print("Órgão:", alerta["sender_name"])

        print()
        print("Headline:")
        print(alerta["headline"])

        print()
        print("Descrição:")
        print(alerta["description"])

        print()
        print("Instrução:")
        print(alerta["instruction"])

        print()
        print("Áreas:")

        for area in alerta["areas"]:

            print("  -", area["description"])

            if area["polygons"]:
                print(
                    "    Polígonos:",
                    len(area["polygons"])
                )

        print()


if __name__ == "__main__":

    root = buscar_feed()

    alertas = extrair_alertas(root)

    mostrar_alertas(alertas)