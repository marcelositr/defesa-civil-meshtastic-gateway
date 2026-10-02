#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import defesa_civil_alertas as dc


def verificar(condicao, mensagem):
    if not condicao:
        raise AssertionError(mensagem)


def main():

    alerta = {
        "headline": "Headline oficial.",
        "description": "Descrição oficial.",
        "instruction": "Instrução oficial.",
    }

    configuracao_original = dc.MESSAGE_FIELDS

    try:
        # ====================================================
        # MODO DEFAULT
        # ====================================================

        dc.MESSAGE_FIELDS = "default"

        verificar(
            dc.montar_texto_oficial(alerta)
            == "Headline oficial.",
            "Default deveria usar o headline.",
        )

        alerta_sem_headline = dict(alerta)
        alerta_sem_headline["headline"] = ""

        verificar(
            dc.montar_texto_oficial(alerta_sem_headline)
            == "Descrição oficial.",
            "Default deveria usar description como fallback.",
        )

        alerta_sem_texto_principal = {
            "headline": "",
            "description": "",
            "instruction": "Instrução oficial.",
        }

        verificar(
            dc.montar_texto_oficial(alerta_sem_texto_principal)
            == "",
            "Default não deveria usar instruction como fallback.",
        )

        # ====================================================
        # SELEÇÃO MANUAL
        # ====================================================

        dc.MESSAGE_FIELDS = ["headline"]

        verificar(
            dc.montar_texto_oficial(alerta)
            == "Headline oficial.",
            "Seleção manual de headline falhou.",
        )

        dc.MESSAGE_FIELDS = ["description"]

        verificar(
            dc.montar_texto_oficial(alerta)
            == "Descrição oficial.",
            "Seleção manual de description falhou.",
        )

        dc.MESSAGE_FIELDS = ["instruction"]

        verificar(
            dc.montar_texto_oficial(alerta)
            == "Instrução oficial.",
            "Seleção manual de instruction falhou.",
        )

        dc.MESSAGE_FIELDS = ["headline", "instruction"]

        verificar(
            dc.montar_texto_oficial(alerta)
            == "Headline oficial.\n\nInstrução oficial.",
            "Combinação de campos falhou.",
        )

        # ====================================================
        # CAMPOS VAZIOS
        # ====================================================

        dc.MESSAGE_FIELDS = [
            "headline",
            "description",
            "instruction",
        ]

        alerta_com_vazios = {
            "headline": "Headline oficial.",
            "description": "",
            "instruction": "Instrução oficial.",
        }

        verificar(
            dc.montar_texto_oficial(alerta_com_vazios)
            == "Headline oficial.\n\nInstrução oficial.",
            "Campos vazios não foram ignorados.",
        )

        alerta_tudo_vazio = {
            "headline": "",
            "description": "",
            "instruction": "",
        }

        verificar(
            dc.montar_texto_oficial(alerta_tudo_vazio)
            == "",
            "Todos os campos vazios deveriam gerar texto vazio.",
        )

        print("TESTE DE CAMPOS DE MENSAGEM")
        print("TESTE PASSOU")

    finally:
        dc.MESSAGE_FIELDS = configuracao_original


if __name__ == "__main__":
    main()
