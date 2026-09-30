#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET


URL = "https://idapfile.mdr.gov.br/idap/api/rss/cap"


NS = {
    "atom": "http://www.w3.org/2005/Atom",
}


print("Baixando alertas da Defesa Civil...")

r = requests.get(URL, timeout=30)
r.raise_for_status()


root = ET.fromstring(r.text)


entries = root.findall("atom:entry", NS)

print("Entradas encontradas:", len(entries))


if not entries:
    print("Nenhum alerta encontrado")
    exit()


entry = entries[0]


print("\n===== TITULO =====")
print(entry.findtext("atom:title", "", NS))


print("\n===== CONTENT RAW =====")

content = entry.find("atom:content", NS)

if content is None:
    print("Sem content")
    exit()


print(ET.tostring(content, encoding="unicode")[:5000])


print("\n===== FILHOS DO CONTENT =====")

for child in content:
    print("TAG:", child.tag)
    print("ATTR:", child.attrib)