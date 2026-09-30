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

                <cap:identifier>TEST-ALERT-001</cap:identifier>

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
                        Teste: alerta inicial.
                    </cap:headline>

                    <cap:description>
                        Alerta inicial para teste do processador.
                    </cap:description>

                    <cap:instruction>
                        Teste controlado.
                    </cap:instruction>

                    <cap:area>

                        <cap:areaDesc>
                            Área de teste
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

                <cap:identifier>TEST-ALERT-002</cap:identifier>

                <cap:sender>teste@defesacivil.local</cap:sender>

                <cap:sent>
                    2026-09-30T18:10:00-03:00
                </cap:sent>

                <cap:status>Actual</cap:status>

                <cap:msgType>Update</cap:msgType>

                <cap:scope>Public</cap:scope>

                <cap:references>
                    teste@defesacivil.local,TEST-ALERT-001,2026-09-30T18:00:00-03:00
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
                        Severe
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
                        Teste: alerta atualizado.
                    </cap:headline>

                    <cap:description>
                        Alerta atualizado para teste do processador.
                    </cap:description>

                    <cap:instruction>
                        Nova instrução de teste.
                    </cap:instruction>

                    <cap:area>

                        <cap:areaDesc>
                            Área de teste
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

                <cap:identifier>TEST-ALERT-003</cap:identifier>

                <cap:sender>teste@defesacivil.local</cap:sender>

                <cap:sent>
                    2026-09-30T18:20:00-03:00
                </cap:sent>

                <cap:status>Actual</cap:status>

                <cap:msgType>Cancel</cap:msgType>

                <cap:scope>Public</cap:scope>

                <cap:references>
                    teste@defesacivil.local,TEST-ALERT-002,2026-09-30T18:10:00-03:00
                </cap:references>

                <cap:info>

                    <cap:category>Met</cap:category>

                    <cap:event>
                        CHUVAS INTENSAS
                    </cap:event>

                    <cap:senderName>
                        Defesa Civil Estadual de São Paulo
                    </cap:senderName>

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
    print("TESTE CAP - ALERT / UPDATE / CANCEL")
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

        for identifier in (
            "TEST-ALERT-001",
            "TEST-ALERT-002",
            "TEST-ALERT-003",
        ):

            dados = estado.get(
                identifier
            )

            print()

            print(
                f"ID: {identifier}"
            )

            if dados is None:

                print(
                    "Estado: não encontrado"
                )

                continue

            print(
                f"Ativo: {dados.get('active')}"
            )

            print(
                f"Afeta localização: "
                f"{dados.get('affected')}"
            )

            if "updated_from" in dados:

                print(
                    f"Atualizado a partir de: "
                    f"{dados['updated_from']}"
                )

            if "updated_by" in dados:

                print(
                    f"Atualizado por: "
                    f"{dados['updated_by']}"
                )

            if "cancelled_by" in dados:

                print(
                    f"Cancelado por: "
                    f"{dados['cancelled_by']}"
                )

        print()

        # ====================================================
        # VALIDAÇÃO
        # ====================================================

        alerta_original = estado.get(
            "TEST-ALERT-001"
        )

        alerta_update = estado.get(
            "TEST-ALERT-002"
        )

        alerta_cancel = estado.get(
            "TEST-ALERT-003"
        )

        sucesso_novo = (
            len(novos) == 1
            and novos[0]["id"]
            == "TEST-ALERT-001"
        )

        sucesso_update = (
            len(atualizados) == 1
            and atualizados[0]["id"]
            == "TEST-ALERT-002"
        )

        sucesso_cancel = (
            alerta_update is not None
            and alerta_update.get(
                "active"
            ) is False
            and alerta_update.get(
                "cancelled_by"
            ) == "TEST-ALERT-003"
        )

        sucesso_original = (
            alerta_original is not None
            and alerta_original.get(
                "active"
            ) is False
        )

        sucesso_cancel_entry = (
            alerta_cancel is None
        )

        print("=" * 80)
        print("VALIDAÇÃO")
        print("=" * 80)

        print()

        print(
            "Alert inicial:      "
            + (
                "OK"
                if sucesso_novo
                else "FALHOU"
            )
        )

        print(
            "Update reconhecido: "
            + (
                "OK"
                if sucesso_update
                else "FALHOU"
            )
        )

        print(
            "Cancel reconhecido: "
            + (
                "OK"
                if sucesso_cancel
                else "FALHOU"
            )
        )

        print(
            "Alerta original inativo: "
            + (
                "OK"
                if sucesso_original
                else "FALHOU"
            )
        )

        print(
            "Cancel não virou novo alerta: "
            + (
                "OK"
                if sucesso_cancel_entry
                else "FALHOU"
            )
        )

        print()

        sucesso = (
            sucesso_novo
            and sucesso_update
            and sucesso_cancel
            and sucesso_original
            and sucesso_cancel_entry
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