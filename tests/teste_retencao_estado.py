#!/usr/bin/env python3

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config
import defesa_civil_alertas as dc


def verificar(condicao, mensagem):
    if not condicao:
        raise AssertionError(mensagem)


def iso_utc(dias_atras=0, dias_a_frente=0):
    agora = datetime.datetime.now(
        datetime.timezone.utc
    )

    momento = agora + datetime.timedelta(
        days=dias_a_frente
    )

    momento -= datetime.timedelta(
        days=dias_atras
    )

    return momento.isoformat()


def main():

    retenção_original = config.STATE_RETENTION_DAYS

    try:
        config.STATE_RETENTION_DAYS = 30

        limite_recente = iso_utc(dias_atras=29)
        limite_antigo = iso_utc(dias_atras=31)

        estado = {
            "EXPIRADO-RECENTE": {
                "active": True,
                "expires": limite_recente,
            },
            "EXPIRADO-ANTIGO": {
                "active": True,
                "expires": limite_antigo,
            },
            "CANCELADO-RECENTE": {
                "active": False,
                "last_seen": limite_recente,
            },
            "CANCELADO-ANTIGO": {
                "active": False,
                "last_seen": limite_antigo,
            },
            "ATIVO": {
                "active": True,
                "expires": iso_utc(dias_a_frente=10),
                "last_seen": limite_antigo,
            },
        }

        removidos = dc.limpar_estado(estado)

        verificar(
            removidos == 2,
            "A limpeza deveria remover exatamente dois registros.",
        )

        verificar(
            "EXPIRADO-RECENTE" in estado,
            "Alerta expirado com menos de 30 dias foi removido.",
        )

        verificar(
            "CANCELADO-RECENTE" in estado,
            "Alerta cancelado com menos de 30 dias foi removido.",
        )

        verificar(
            "EXPIRADO-ANTIGO" not in estado,
            "Alerta expirado com mais de 30 dias permaneceu.",
        )

        verificar(
            "CANCELADO-ANTIGO" not in estado,
            "Alerta cancelado com mais de 30 dias permaneceu.",
        )

        verificar(
            "ATIVO" in estado,
            "Alerta ainda ativo foi removido indevidamente.",
        )

        print("TESTE DE RETENÇÃO DO ESTADO")
        print("Retenção configurada: 30 dias")
        print("Registros removidos: 2")
        print("TESTE PASSOU")

    finally:
        config.STATE_RETENTION_DAYS = retenção_original


if __name__ == "__main__":
    main()
