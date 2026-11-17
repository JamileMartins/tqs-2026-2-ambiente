# -*- coding: utf-8 -*-
"""Cancelamento de reserva com notificacao.

Sistema de Agendamento de Laboratorios - IFCE Campus Caninde - 2026.2

VOCE VAI ESCREVER ESTE ARQUIVO, um ciclo de TDD por vez.
Nao escreva tudo de uma vez: siga a ordem dos requisitos do roteiro.
"""

CONFIRMADA = "CONFIRMADA"
CANCELADA = "CANCELADA"
PRAZO_HORAS = 4


def cancelar_reserva(reserva, horas_ate_inicio, notificador):
    """Cancela uma reserva confirmada e notifica o professor responsavel.

    reserva            -- dicionario com as chaves 'estado' e 'professor'
    horas_ate_inicio   -- horas que faltam para o inicio do horario
    notificador        -- objeto com o metodo enviar(destinatario, mensagem)

    Devolve a tupla (cancelada, motivo).
    """
    # Comece pelo ciclo 1 do roteiro. Escreva o teste ANTES de escrever aqui.
    raise NotImplementedError("ciclo 1 ainda nao implementado")
