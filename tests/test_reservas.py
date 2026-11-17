# -*- coding: utf-8 -*-
"""Testes de demonstração do módulo de reservas.

Este arquivo existe para dois fins:

1. Confirmar que o ambiente está funcionando — basta rodar `pytest` e ver saída.
2. Demonstrar `pytest.mark.parametrize`, que é a ferramenta usada para escrever
   casos derivados por partição de equivalência e análise de valor-limite.

ATENÇÃO: alguns testes deste arquivo FALHAM de propósito. A falha não é do
ambiente: é um defeito real do módulo reservas.py, e encontrá-lo é parte da
disciplina. Não "conserte" o teste para ele passar.
"""

from datetime import datetime, timedelta

import pytest

from reservas import (
    CANCELADA,
    CONFIRMADA,
    EM_USO,
    EXPIRADA,
    SOLICITADA,
    Reserva,
    processar_evento,
)

INICIO = datetime(2026, 10, 1, 19, 0)
FIM = datetime(2026, 10, 1, 22, 0)


def nova_reserva(estado=SOLICITADA, laboratorio="LAB-3"):
    r = Reserva("R1", laboratorio, INICIO, FIM, "prof.jamile")
    r.estado = estado
    return r


# ---------------------------------------------------------------- T1 e T2

def test_t1_confirmar_sem_conflito():
    r = nova_reserva()
    processar_evento(r, "confirmar", agora=INICIO - timedelta(days=1), confirmadas=[])
    assert r.estado == CONFIRMADA


def test_t2_confirmar_com_horario_ocupado():
    existente = nova_reserva(estado=CONFIRMADA)
    r = nova_reserva()
    processar_evento(r, "confirmar", agora=INICIO - timedelta(days=1),
                     confirmadas=[existente])
    assert r.estado == CANCELADA


# ---------------------------------------------------------------- T5 e T6

def test_t5_presenca_dentro_do_prazo():
    r = nova_reserva(estado=CONFIRMADA)
    processar_evento(r, "registrar_presenca", agora=INICIO + timedelta(minutes=15))
    assert r.estado == EM_USO


def test_t6_sem_presenca_expira():
    r = nova_reserva(estado=CONFIRMADA)
    processar_evento(r, "registrar_presenca", agora=INICIO + timedelta(minutes=21))
    assert r.estado == EXPIRADA


# ------------------------------------------- T4: análise de valor-limite
#
# O requisito R02 diz: "cancelar até 4 horas antes do início".
# "Até 4 horas" INCLUI exatamente 4 horas.
#
# Os três casos abaixo são os valores-limite dessa fronteira. Um deles falha.
# Descobrir por que é o exercício.

@pytest.mark.parametrize(
    "horas_antes, deve_cancelar",
    [
        (5.0, True),      # bem dentro do prazo
        (4.0, True),      # exatamente na fronteira — o requisito permite
        (3.9, False),     # fora do prazo
    ],
    ids=["5h-antes", "4h-antes-limite", "3h54-antes"],
)
def test_t4_cancelamento_nos_valores_limite(horas_antes, deve_cancelar):
    r = nova_reserva(estado=CONFIRMADA)
    agora = INICIO - timedelta(hours=horas_antes)
    processar_evento(r, "cancelar", agora=agora)
    if deve_cancelar:
        assert r.estado == CANCELADA, (
            "com %.1f h de antecedência a reserva deveria ser cancelada" % horas_antes
        )
    else:
        assert r.estado == CONFIRMADA
