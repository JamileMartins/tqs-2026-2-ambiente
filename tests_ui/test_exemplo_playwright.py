# -*- coding: utf-8 -*-
"""Exemplo minimo de teste de interface com Playwright.

Serve para dois fins:

1. Confirmar que o ambiente esta funcionando - rode e veja passar.
2. Mostrar a FORMA de um teste de interface: abrir a pagina, preencher
   campos, clicar e verificar o que apareceu na tela.

Este arquivo NAO testa as regras de negocio. Derivar os casos que testam
os requisitos e o trabalho da Pratica 11.

Rodar:  pytest tests_ui -v
"""
import pathlib

import pytest
from playwright.sync_api import sync_playwright

PAGINA = (pathlib.Path(__file__).resolve().parent.parent / "web" / "agendamento.html").as_uri()


@pytest.fixture(scope="module")
def pagina():
    """Abre o navegador uma vez para todos os testes deste arquivo."""
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        aba = navegador.new_page()
        yield aba
        navegador.close()


def solicitar(aba, duracao, antecedencia, laboratorio):
    """Preenche o formulario, envia e devolve o texto do resultado.

    Use esta funcao nos testes que voce escrever.
    """
    aba.goto(PAGINA)
    aba.fill("#duracao", str(duracao))
    aba.fill("#antecedencia", str(antecedencia))
    aba.fill("#laboratorio", laboratorio)
    aba.click("#enviar")
    return aba.inner_text("#resultado")


def test_a_pagina_abre_e_responde(pagina):
    """O formulario carrega, aceita dados e devolve alguma resposta."""
    pagina.goto(PAGINA)
    assert "Agendamento" in pagina.title()
    texto = solicitar(pagina, 2, 48, "Lab 1")
    assert texto, "a pagina nao devolveu nenhuma resposta"
    assert "Preencha" not in texto, "a pagina nao reagiu ao clique"
