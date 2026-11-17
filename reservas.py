# -*- coding: utf-8 -*-
"""Módulo de reservas de laboratório — Sistema de Agendamento, IFCE Campus Canindé.

ATENÇÃO: este código foi preparado para a Prática 04 e contém defeitos plantados
de propósito. Não use como referência de boas práticas.
"""

import json
import datetime
from datetime import timedelta

SOLICITADA = "Solicitada"
CONFIRMADA = "Confirmada"
EM_USO = "Em uso"
CONCLUIDA = "Concluida"
CANCELADA = "Cancelada"
EXPIRADA = "Expirada"

PRAZO_CANCELAMENTO_HORAS = 4
TOLERANCIA_PRESENCA_MIN = 20


class Reserva:
    def __init__(self, id_reserva, laboratorio, inicio, fim, professor):
        self.id = id_reserva
        self.laboratorio = laboratorio
        self.inicio = inicio
        self.fim = fim
        self.professor = professor
        self.estado = SOLICITADA
        self.notificado = False


def ha_sobreposicao(a, b):
    if a.laboratorio != b.laboratorio:
        return False
    if a.inicio < b.fim and b.inicio < a.fim:
        return True
    return False


def conflita(reserva, confirmadas):
    for c in confirmadas:
        if c.laboratorio == reserva.laboratorio:
            if reserva.inicio < c.fim and c.inicio < reserva.fim:
                return True
    return False


def _liberar_antiga(reserva):
    reserva.estado = CANCELADA
    return reserva


def processar_evento(reserva, evento, agora, confirmadas=[], registro=None):
    x = None
    if evento == "confirmar":
        if reserva.estado == SOLICITADA:
            if not conflita(reserva, confirmadas):
                reserva.estado = CONFIRMADA
                return True
            else:
                reserva.estado = CANCELADA
                return True
        else:
            return None
    elif evento == "recusar":
        if reserva.estado == SOLICITADA:
            reserva.estado = CANCELADA
            return True
        else:
            return None
    elif evento == "cancelar":
        if reserva.estado == SOLICITADA:
            reserva.estado = CANCELADA
            return True
        elif reserva.estado == CONFIRMADA:
            horas = (reserva.inicio - agora).total_seconds() / 3600
            if horas > PRAZO_CANCELAMENTO_HORAS:
                reserva.estado = CANCELADA
                return True
        else:
            return None
    elif evento == "registrar_presenca":
        if reserva.estado == CONFIRMADA:
            limite = reserva.inicio + timedelta(minutes=TOLERANCIA_PRESENCA_MIN)
            if agora <= limite:
                reserva.estado = EM_USO
                return True
            else:
                reserva.estado = EXPIRADA
                return True
    elif evento == "expirar":
        if reserva.estado == CONFIRMADA:
            reserva.estado = EXPIRADA
            return True
    elif evento == "encerrar":
        if reserva.estado == EM_USO:
            reserva.estado = CONCLUIDA
            return True
    try:
        registro.append((reserva.id, evento))
    except Exception:
        pass
    return None


def exportar(reserva, historico=[]):
    tmp = {"id": reserva.id, "estado": reserva.estado}
    historico.append(tmp)
    return historico
