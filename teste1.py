#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET

URL = "https://idapfile.mdr.gov.br/idap/api/rss/cap"

ATOM = "http://www.w3.org/2005/Atom"
CAP = "urn:oasis:names:tc:emergency:cap:1.2"

NS = {
    "atom": ATOM,
    "cap": CAP,
}

root = ET.fromstring(
    requests.get(URL, timeout=30).content
)

for entry in root.findall("atom:entry", NS):

    content = entry.find("atom:content", NS)
    alert = content.find("cap:alert", NS)
    info = alert.find("cap:info", NS)

    area = info.find("cap:area", NS)

    if area is None:
        continue

    area_desc = area.findtext("cap:areaDesc", "", NS)

    if area_desc == "SÃO PAULO/SP":

        identifier = alert.findtext(
            "cap:identifier", "", NS
        )

        headline = info.findtext(
            "cap:headline", "", NS
        )

        polygon = area.findtext(
            "cap:polygon", "", NS
        )

        print("=" * 70)
        print("ID:", identifier)
        print("HEADLINE:", headline)
        print()
        print("POLYGON:")
        print(polygon)
        print("=" * 70)

        break
		