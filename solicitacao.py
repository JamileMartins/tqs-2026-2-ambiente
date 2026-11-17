# -*- coding: utf-8 -*-
"""Validacao da solicitacao de reserva.

Sistema de Agendamento e Controle de Uso de Laboratorios
IFCE - Campus Caninde - Teste e Qualidade de Software - 2026.2

Alvo da Pratica 08. Nao altere este arquivo.
"""


def validar_solicitacao(duracao, antecedencia_horas, laboratorio):
    """Valida os campos de uma solicitacao de reserva.

    duracao             -- duracao pedida, em horas-aula inteiras
    antecedencia_horas  -- horas entre a solicitacao e o inicio do horario
    laboratorio         -- identificacao do laboratorio, texto

    Devolve (valido, lista_de_erros).
    """
    erros = []
    if duracao < 1:
        erros.append("duracao_minima")
    if duracao > 4:
        erros.append("duracao_maxima")
    if antecedencia_horas < 24:
        erros.append("antecedencia")
    if not laboratorio:
        erros.append("laboratorio")
    if erros:
        return False, erros
    return True, []
