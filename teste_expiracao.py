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

                <cap:identifier>TEST-EXPIRED-001</cap:identifier>

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
                        2020-01-01T00:00:00Z
                    </cap:expires>

                    <cap:headline>
                        Teste: alerta expirado.
                    </cap:headline>

                    <cap:description>
                        Este alerta possui uma data de expiração no passado.
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

</feed>
"""


# ============================================================
# EXECUÇÃO
# ============================================================

def main():

    print("=" * 80)
    print("TESTE CAP - ALERTA EXPIRADO")
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

        alerta = estado.get(
            "TEST-EXPIRED-001"
        )

        print()

        print(
            "ID: TEST-EXPIRED-001"
        )

        if alerta is None:

            print(
                "Estado: não encontrado"
            )

        else:

            print(
                f"Ativo: "
                f"{alerta.get('active')}"
            )

            print(
                f"Expirado: "
                f"{alerta.get('expired')}"
            )

            print(
                f"Afeta localização: "
                f"{alerta.get('affected')}"
            )

        print()

        # ====================================================
        # VALIDAÇÃO
        # ====================================================

        sucesso_nao_novo = (
            len(novos) == 0
        )

        sucesso_nao_atualizado = (
            len(atualizados) == 0
        )

        sucesso_estado = (
            alerta is None
            or (
                alerta.get("active") is False
                and alerta.get("expired") is True
            )
        )

        print("=" * 80)
        print("VALIDAÇÃO")
        print("=" * 80)

        print()

        print(
            "Alerta expirado não entrou como novo: "
            + (
                "OK"
                if sucesso_nao_novo
                else "FALHOU"
            )
        )

        print(
            "Alerta expirado não gerou atualização: "
            + (
                "OK"
                if sucesso_nao_atualizado
                else "FALHOU"
            )
        )

        print(
            "Estado marcado como expirado/inativo: "
            + (
                "OK"
                if sucesso_estado
                else "FALHOU"
            )
        )

        print()

        sucesso = (
            sucesso_nao_novo
            and sucesso_nao_atualizado
            and sucesso_estado
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
