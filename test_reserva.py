# -*- coding: utf-8 -*-
"""Suite do kata de TDD. Voce escreve os testes aqui, um ciclo por vez."""
from reserva import cancelar_reserva, CONFIRMADA, CANCELADA


# ---------------------------------------------------------------- dubles
# Os tres dubles ja vem prontos para voce nao gastar tempo com infraestrutura.
# Leia os tres antes de comecar: a Parte C do roteiro pergunta sobre eles.

class NotificadorMudo:
    """STUB: aceita a chamada e nao faz nada. Serve so para o codigo rodar."""
    def enviar(self, destinatario, mensagem):
        pass


class NotificadorEspiao:
    """ESPIAO: deixa a chamada acontecer e REGISTRA para inspecao depois."""
    def __init__(self):
        self.chamadas = []

    def enviar(self, destinatario, mensagem):
        self.chamadas.append((destinatario, mensagem))


class NotificadorQueFalha:
    """STUB de erro: simula o servico de e-mail fora do ar."""
    def enviar(self, destinatario, mensagem):
        raise ConnectionError("servico de e-mail indisponivel")


def nova_reserva(estado=CONFIRMADA):
    """Auxiliar: devolve uma reserva nova para cada teste."""
    return {"estado": estado, "professor": "professor@ifce.edu.br"}


# ---------------------------------------------------------------- ciclo 1
def test_cancela_reserva_confirmada():
    r = nova_reserva()
    ok, motivo = cancelar_reserva(r, 10, NotificadorMudo())
    assert ok is True
    assert motivo == "cancelada"
    assert r["estado"] == CANCELADA


# ---------------------------------------------------------------- ciclo 2
# escreva aqui o teste do ciclo 2, antes de mexer no reserva.py
