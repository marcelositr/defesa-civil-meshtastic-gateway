#!/usr/bin/env python3

import json
import os
import tempfile
import xml.etree.ElementTree as ET

import defesa_civil_alertas as dc


# ============================================================
# CONFIGURAÇÃO DO TESTE
# ============================================================

TEST_LAT = -22.739
TEST_LON = -45.591

ATOM_NS = "http://www.w3.org/2005/Atom"
CAP_NS = "urn:oasis:names:tc:emergency:cap:1.2"

NS = {
    "atom": ATOM_NS,
    "cap": CAP_NS,
}


# ============================================================
# CAP DE TESTE
# ============================================================

CAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:cap="urn:oasis:names:tc:emergency:cap:1.2">

    <entry>
        <content type="application/xml">
            <cap:alert>

                <cap:identifier>TEST-OUTSIDE-001</cap:identifier>

                <cap:sender>teste@defesacivil.local</cap:sender>

                <cap:sent>
                    2026-09-30T18:00:00-03:00
                </cap:sent>

                <cap:status>Actual</cap:status>

                <cap:msgType>Alert</cap:msgType>

                <cap:scope>Public</cap:scope>

                <cap:info>

                    <cap:category>Met</cap:category>

                    <cap:event>
                        CHUVAS INTENSAS
                    </cap:event>

                    <cap:urgency>
                        Immediate
                    </cap:urgency>

                    <cap:severity>
                        Moderate
                    </cap:severity>

                    <cap:certainty>
                        Observed
                    </cap:certainty>

                    <cap:senderName>
                        Defesa Civil Estadual de São Paulo
                    </cap:senderName>

                    <cap:onset>
                        2026-09-30T18:00:00-03:00
                    </cap:onset>

                    <cap:expires>
                        2099-12-31T23:59:59Z
                    </cap:expires>

                    <cap:headline>
                        Teste: alerta inicial dentro da área.
                    </cap:headline>

                    <cap:description>
                        Alerta inicialmente atinge a localização.
                    </cap:description>

                    <cap:instruction>
                        Teste controlado.
                    </cap:instruction>

                    <cap:area>

                        <cap:areaDesc>
                            Área inicial
                        </cap:areaDesc>

                        <cap:polygon>
                            -22.500,-45.800
                            -22.500,-45.400
                            -23.000,-45.400
                            -23.000,-45.800
                            -22.500,-45.800
                        </cap:polygon>

                    </cap:area>

                </cap:info>

            </cap:alert>
        </content>
    </entry>


    <entry>
        <content type="application/xml">
            <cap:alert>

                <cap:identifier>TEST-OUTSIDE-002</cap:identifier>

                <cap:sender>teste@defesacivil.local</cap:sender>

                <cap:sent>
                    2026-09-30T18:10:00-03:00
                </cap:sent>

                <cap:status>Actual</cap:status>

                <cap:msgType>Update</cap:msgType>

                <cap:scope>Public</cap:scope>

                <cap:references>
                    teste@defesacivil.local,TEST-OUTSIDE-001,2026-09-30T18:00:00-03:00
                </cap:references>

                <cap:info>

                    <cap:category>Met</cap:category>

                    <cap:event>
                        CHUVAS INTENSAS
                    </cap:event>

                    <cap:urgency>
                        Immediate
                    </cap:urgency>

                    <cap:severity>
                        Moderate
                    </cap:severity>

                    <cap:certainty>
                        Observed
                    </cap:certainty>

                    <cap:senderName>
                        Defesa Civil Estadual de São Paulo
                    </cap:senderName>

                    <cap:onset>
                        2026-09-30T18:00:00-03:00
                    </cap:onset>

                    <cap:expires>
                        2099-12-31T23:59:59Z
                    </cap:expires>

                    <cap:headline>
                        Teste: alerta deixou de atingir a localização.
                    </cap:headline>

                    <cap:description>
                        O polígono foi deslocado para fora da localização.
                    </cap:description>

                    <cap:instruction>
                        Não transmitir alerta para esta localização.
                    </cap:instruction>

                    <cap:area>

                        <cap:areaDesc>
                            Nova área fora da localização
                        </cap:areaDesc>

                        <cap:polygon>
                            -20.000,-47.000
                            -20.000,-46.500
                            -20.500,-46.500
                            -20.500,-47.000
                            -20.000,-47.000
                        </cap:polygon>

                    </cap:area>

                </cap:info>

            </cap:alert>
        </content>
    </entry>

</feed>
"""


# ============================================================
# EXECUÇÃO
# ============================================================

def main():

    print("=" * 80)
    print("TESTE CAP - UPDATE DEIXA DE ATINGIR A LOCALIZAÇÃO")
    print("=" * 80)

    print()

    root = ET.fromstring(
        CAP_XML
    )

    entries = root.findall(
        "atom:entry",
        NS,
    )

    print(
        f"Entradas de teste: {len(entries)}"
    )

    print()

    arquivo_original = dc.STATE_FILE

    estado_teste = None

    try:

        with tempfile.NamedTemporaryFile(
            suffix=".json",
            delete=False,
        ) as arquivo:

            estado_teste = arquivo.name

        dc.STATE_FILE = estado_teste

        novos, atualizados, ignorados = (
            dc.processar_alertas(
                entries,
                TEST_LAT,
                TEST_LON,
            )
        )

        print("=" * 80)
        print("RESULTADO DO PROCESSAMENTO")
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

        print("=" * 80)
        print("ESTADO FINAL")
        print("=" * 80)

        with open(
            estado_teste,
            "r",
            encoding="utf-8",
        ) as arquivo:

            estado = json.load(
                arquivo
            )

        alerta_original = estado.get(
            "TEST-OUTSIDE-001"
        )

        alerta_update = estado.get(
            "TEST-OUTSIDE-002"
        )

        print()

        print(
            "ID: TEST-OUTSIDE-001"
        )

        if alerta_original is None:

            print(
                "Estado: não encontrado"
            )

        else:

            print(
                f"Ativo: "
                f"{alerta_original.get('active')}"
            )

            print(
                f"Afeta localização: "
                f"{alerta_original.get('affected')}"
            )

            if "updated_by" in alerta_original:

                print(
                    f"Atualizado por: "
                    f"{alerta_original['updated_by']}"
                )

        print()

        print(
            "ID: TEST-OUTSIDE-002"
        )

        if alerta_update is None:

            print(
                "Estado: não encontrado"
            )

        else:

            print(
                f"Ativo: "
                f"{alerta_update.get('active')}"
            )

            print(
                f"Afeta localização: "
                f"{alerta_update.get('affected')}"
            )

            if "updated_from" in alerta_update:

                print(
                    f"Atualizado a partir de: "
                    f"{alerta_update['updated_from']}"
                )

        print()

        # ====================================================
        # VALIDAÇÃO
        # ====================================================

        sucesso_novo = (
            len(novos) == 1
            and novos[0]["id"]
            == "TEST-OUTSIDE-001"
        )

        sucesso_update_nao_transmitido = (
            len(atualizados) == 0
        )

        sucesso_original = (
            alerta_original is not None
            and alerta_original.get(
                "active"
            ) is False
            and alerta_original.get(
                "affected"
            ) is False
            and alerta_original.get(
                "updated_by"
            ) == "TEST-OUTSIDE-002"
        )

        sucesso_update = (
            alerta_update is not None
            and alerta_update.get(
                "active"
            ) is False
            and alerta_update.get(
                "affected"
            ) is False
            and alerta_update.get(
                "updated_from"
            ) == "TEST-OUTSIDE-001"
        )

        print("=" * 80)
        print("VALIDAÇÃO")
        print("=" * 80)

        print()

        print(
            "Alert inicial entrou: "
            + (
                "OK"
                if sucesso_novo
                else "FALHOU"
            )
        )

        print(
            "Update não gerou transmissão: "
            + (
                "OK"
                if sucesso_update_nao_transmitido
                else "FALHOU"
            )
        )

        print(
            "Alerta original ficou inativo: "
            + (
                "OK"
                if sucesso_original
                else "FALHOU"
            )
        )

        print(
            "Update ficou inativo: "
            + (
                "OK"
                if sucesso_update
                else "FALHOU"
            )
        )

        print()

        sucesso = (
            sucesso_novo
            and sucesso_update_nao_transmitido
            and sucesso_original
            and sucesso_update
        )

        if sucesso:

            print(
                "TESTE PASSOU"
            )

        else:

            print(
                "TESTE FALHOU"
            )

    finally:

        dc.STATE_FILE = arquivo_original

        if estado_teste is not None:

            try:

                os.unlink(
                    estado_teste
                )

            except OSError:

                pass


if __name__ == "__main__":
    main()
