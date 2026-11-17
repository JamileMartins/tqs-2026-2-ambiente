# -*- coding: utf-8 -*-
"""Mensagens de erro compartilhadas. Nao e preciso abrir este arquivo."""
import os
import sys


def dica_de_pasta():
    return ("A pasta atual e:\n      %s\n"
            "   Use o comando cd para entrar na pasta onde estao os arquivos.\n"
            "   No Windows: clique na barra de endereco do Explorador de Arquivos,\n"
            "   digite cmd e tecle Enter." % os.getcwd())


def explicar(erro, caminho):
    """Traduz uma excecao de carregamento para uma mensagem util."""
    if isinstance(erro, FileNotFoundError):
        return ("Arquivo nao encontrado: %s\n   %s" % (caminho, dica_de_pasta()))
    if isinstance(erro, SyntaxError):
        return ("Erro de sintaxe em %s, linha %s:\n      %s\n"
                "   %s\n"
                "   Corrija a linha e rode de novo."
                % (erro.filename or caminho, erro.lineno,
                   (erro.text or "").rstrip(), erro.msg))
    if isinstance(erro, ModuleNotFoundError):
        faltando = getattr(erro, "name", "") or ""
        if faltando.split(".")[0] in ("pytest", "unittest2", "nose", "mock"):
            return ("O arquivo %s tem a linha 'import %s', e esta pratica nao usa\n"
                    "   essa biblioteca. Apague a linha: os testes aqui sao funcoes\n"
                    "   comuns com assert, executadas pelo rodar.py." % (caminho, faltando))
        return ("O arquivo %s importa '%s', que nao esta instalado.\n"
                "   Esta pratica usa apenas a biblioteca padrao do Python."
                % (caminho, faltando))
    if isinstance(erro, ImportError):
        return ("Falha ao importar algo em %s:\n      %s\n"
                "   Confira se os nomes importados existem no reserva.py."
                % (caminho, erro))
    return "%s ao carregar %s:\n      %s" % (type(erro).__name__, caminho, erro)


def exige_python_39():
    if sys.version_info < (3, 9):
        print("ERRO: esta ferramenta precisa de Python 3.9 ou mais novo.")
        print("   Voce esta usando a versao %d.%d."
              % (sys.version_info[0], sys.version_info[1]))
        print("   Confira com:  python --version")
        print("   Se a maquina tiver outra versao instalada, tente:  py -3 rodar.py")
        sys.exit(2)
