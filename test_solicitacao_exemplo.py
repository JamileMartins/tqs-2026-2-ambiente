# -*- coding: utf-8 -*-
"""Suite de exemplo da Pratica 08 - tres casos."""
from solicitacao import validar_solicitacao


def test_tudo_valido():
    assert validar_solicitacao(3, 48, "Lab 1") == (True, [])


def test_duracao_curta_sem_antecedencia_sem_laboratorio():
    ok, erros = validar_solicitacao(0, 10, "")
    assert ok is False
    assert set(erros) == {"duracao_minima", "antecedencia", "laboratorio"}


def test_duracao_longa():
    ok, erros = validar_solicitacao(7, 48, "Lab 2")
    assert ok is False and erros == ["duracao_maxima"]
