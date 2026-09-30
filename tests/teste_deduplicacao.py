#!/usr/bin/env python3

import json
import os
import tempfile
import xml.etree.ElementTree as ET
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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

                <cap:identifier>TEST-DEDUP-001</cap:identifier>

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
                        Teste: alerta de deduplicação.
                    </cap:headline>

                    <cap:description>
                        Este alerta deve ser processado somente uma vez.
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
    print("TESTE DE DEDUPLICAÇÃO ENTRE EXECUÇÕES")
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

        # ====================================================
        # PRIMEIRA EXECUÇÃO
        # ====================================================

        print("=" * 80)
        print("PRIMEIRA EXECUÇÃO")
        print("=" * 80)

        novos_1, atualizados_1, ignorados_1 = (
            dc.processar_alertas(
                entries,
                TEST_LAT,
                TEST_LON,
            )
        )

        print()

        print(
            f"Novos:        {len(novos_1)}"
        )

        print(
            f"Atualizados:  {len(atualizados_1)}"
        )

        print(
            f"Ignorados:    {len(ignorados_1)}"
        )

        print()

        # ====================================================
        # SEGUNDA EXECUÇÃO
        # ====================================================

        print("=" * 80)
        print("SEGUNDA EXECUÇÃO")
        print("=" * 80)

        novos_2, atualizados_2, ignorados_2 = (
            dc.processar_alertas(
                entries,
                TEST_LAT,
                TEST_LON,
            )
        )

        print()

        print(
            f"Novos:        {len(novos_2)}"
        )

        print(
            f"Atualizados:  {len(atualizados_2)}"
        )

        print(
            f"Ignorados:    {len(ignorados_2)}"
        )

        print()

        # ====================================================
        # ESTADO FINAL
        # ====================================================

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
            "TEST-DEDUP-001"
        )

        print()

        if alerta is None:

            print(
                "Estado: não encontrado"
            )

        else:

            print(
                "ID: TEST-DEDUP-001"
            )

            print(
                f"Ativo: "
                f"{alerta.get('active')}"
            )

            print(
                f"Afeta localização: "
                f"{alerta.get('affected')}"
            )

            print(
                f"Assinatura registrada: "
                f"{bool(alerta.get('signature'))}"
            )

        print()

        # ====================================================
        # VALIDAÇÃO
        # ====================================================

        sucesso_primeira = (
            len(novos_1) == 1
            and novos_1[0]["id"]
            == "TEST-DEDUP-001"
            and len(atualizados_1) == 0
        )

        sucesso_segunda = (
            len(novos_2) == 0
            and len(atualizados_2) == 0
            and len(ignorados_2) == 1
            and ignorados_2[0]["id"]
            == "TEST-DEDUP-001"
        )

        sucesso_estado = (
            alerta is not None
            and alerta.get("active") is True
            and alerta.get("affected") is True
            and bool(alerta.get("signature"))
        )

        print("=" * 80)
        print("VALIDAÇÃO")
        print("=" * 80)

        print()

        print(
            "Primeira execução gerou novo alerta: "
            + (
                "OK"
                if sucesso_primeira
                else "FALHOU"
            )
        )

        print(
            "Segunda execução não repetiu o alerta: "
            + (
                "OK"
                if sucesso_segunda
                else "FALHOU"
            )
        )

        print(
            "Estado persistido corretamente: "
            + (
                "OK"
                if sucesso_estado
                else "FALHOU"
            )
        )

        print()

        sucesso = (
            sucesso_primeira
            and sucesso_segunda
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
