# -*- coding: utf-8 -*-
"""Verificador do ambiente - Teste e Qualidade de Software, IFCE Caninde.

Confere se o ambiente esta pronto para as praticas. Rode na raiz do
repositorio, dentro do Codespace:

    python verificar_ambiente.py
"""
import os
import subprocess
import sys

OK, FALHA = "[ OK ]", "[FALHA]"
problemas = []


def diga(marca, titulo, detalhe=""):
    print("%s %s" % (marca, titulo))
    if detalhe:
        for linha in str(detalhe).splitlines():
            print("        " + linha)


def rodar(comando):
    try:
        r = subprocess.run(comando, capture_output=True, text=True, timeout=300)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except FileNotFoundError:
        return 127, "comando nao encontrado"
    except subprocess.TimeoutExpired:
        return 124, "tempo esgotado"


print("=" * 64)
print("Verificacao do ambiente - IFCE Campus Caninde - 2026.2")
print("=" * 64)
print("Pasta atual: %s" % os.getcwd())
print()

v = sys.version_info
if v >= (3, 9):
    diga(OK, "Python %d.%d" % (v[0], v[1]))
else:
    diga(FALHA, "Python %d.%d - a disciplina precisa de 3.9 ou mais novo" % (v[0], v[1]))
    problemas.append("versao do Python")

faltando = [f for f in ("solicitacao.py", "reserva.py", "mutantes.py", "rodar.py",
                        "_erros.py", "web/agendamento.html") if not os.path.exists(f)]
if faltando:
    diga(FALHA, "Arquivos faltando", "\n".join(faltando))
    problemas.append("arquivos do repositorio")
else:
    diga(OK, "Arquivos do repositorio presentes")

cod, saida = rodar([sys.executable, "rodar.py", "test_reserva.py"])
if "passaram" in saida or "falharam" in saida:
    diga(OK, "rodar.py funciona")
else:
    diga(FALHA, "rodar.py nao rodou", saida[-300:])
    problemas.append("rodar.py")

cod, saida = rodar([sys.executable, "mutantes.py", "solicitacao.py",
                    "test_solicitacao_exemplo.py"])
if "ESCORE" in saida:
    diga(OK, "mutantes.py funciona")
else:
    diga(FALHA, "mutantes.py nao rodou", saida[-300:])
    problemas.append("mutantes.py")

cod, saida = rodar([sys.executable, "-m", "pytest", "--version"])
if cod == 0:
    diga(OK, "pytest instalado", saida.strip().splitlines()[0])
else:
    diga(FALHA, "pytest nao esta instalado", "rode: pip install -r requirements.txt")
    problemas.append("pytest")

try:
    import playwright  # noqa: F401
    diga(OK, "modulo playwright importado")
    tem = True
except ImportError:
    diga(FALHA, "playwright nao esta instalado", "rode: pip install -r requirements.txt")
    problemas.append("playwright")
    tem = False

if tem:
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            nav = p.chromium.launch()
            nav.close()
        diga(OK, "o navegador Chromium sobe corretamente")
    except Exception as erro:
        texto_erro = str(erro)
        if "so." in texto_erro or "shared librar" in texto_erro or "shared object" in texto_erro:
            diga(FALHA, "o Chromium nao sobe: faltam bibliotecas de sistema",
                 "rode:  python -m playwright install --with-deps chromium\n"
                 "e depois rode este verificador de novo")
        elif "Executable doesn" in texto_erro:
            diga(FALHA, "o Chromium nao foi baixado",
                 "rode:  python -m playwright install chromium")
        else:
            diga(FALHA, "o navegador nao subiu", texto_erro[:300])
        problemas.append("navegador do Playwright")
    else:
        cod, saida = rodar([sys.executable, "-m", "pytest",
                            "tests_ui/test_exemplo_playwright.py", "-q"])
        if "1 passed" in saida:
            diga(OK, "o teste de exemplo da interface passou")
        else:
            diga(FALHA, "o teste de exemplo da interface nao passou", saida[-400:])
            problemas.append("teste de exemplo")

print()
print("=" * 64)
if not problemas:
    print("VEREDITO: ambiente pronto para a pratica.")
else:
    print("VEREDITO: ha %d ponto(s) a resolver:" % len(problemas))
    for p in problemas:
        print("   - %s" % p)
    print()
    print("Mostre esta saida inteira para a professora.")
print("=" * 64)
