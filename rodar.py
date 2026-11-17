# -*- coding: utf-8 -*-
"""Executor de testes da disciplina - biblioteca padrao, sem instalar nada.

Teste e Qualidade de Software - IFCE Campus Caninde - 2026.2

Encontra todas as funcoes que comecam com "test" nos arquivos indicados,
executa cada uma e informa o resultado. Use no ciclo do TDD.

Uso:
    python rodar.py                       roda test_reserva.py
    python rodar.py test_reserva.py       roda o arquivo indicado
    python rodar.py test_a.py test_b.py   roda varios
    python rodar.py --ajuda               mostra esta mensagem
"""
import inspect
import sys
import types

try:
    import _erros
except ImportError:
    print("ERRO: o arquivo _erros.py nao esta nesta pasta.")
    print("   Ele faz parte do pacote da pratica. Descompacte o zip de novo,")
    print("   mantendo os cinco arquivos juntos na mesma pasta.")
    raise SystemExit(2)

PADRAO = ["test_reserva.py"]


def carregar(caminho):
    with open(caminho, encoding="utf-8") as fp:
        fonte = fp.read()
    nome = caminho[:-3] if caminho.endswith(".py") else caminho
    modulo = types.ModuleType(nome)
    modulo.__file__ = caminho
    exec(compile(fonte, caminho, "exec"), modulo.__dict__)
    return modulo


def funcoes_de_teste(modulo, caminho, avisos):
    encontradas = []
    for nome in sorted(vars(modulo)):
        if not nome.startswith("test"):
            continue
        funcao = getattr(modulo, nome)
        if not callable(funcao):
            continue
        try:
            obrigatorios = [
                p for p in inspect.signature(funcao).parameters.values()
                if p.default is inspect.Parameter.empty
                and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
            ]
        except (TypeError, ValueError):
            obrigatorios = []
        if obrigatorios:
            avisos.append(
                "%s em %s recebe parametro(s): %s.\n"
                "      Nesta pratica as funcoes de teste nao recebem parametros.\n"
                "      Escreva um teste para cada caso, ou use um laco dentro do teste."
                % (nome, caminho, ", ".join(p.name for p in obrigatorios)))
            continue
        encontradas.append((nome, funcao))
    return encontradas


def main(argv):
    _erros.exige_python_39()
    if "--ajuda" in argv or "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    arquivos = argv or PADRAO
    print("Executor de testes - IFCE Campus Caninde")
    print("-" * 62)
    passou, falhou, avisos = 0, [], []
    for caminho in arquivos:
        try:
            modulo = carregar(caminho)
        except Exception as erro:
            print("ERRO: " + _erros.explicar(erro, caminho))
            return 1
        testes = funcoes_de_teste(modulo, caminho, avisos)
        if not testes and not avisos:
            print("  AVISO: nenhuma funcao comecando com 'test' em %s" % caminho)
        for nome, funcao in testes:
            try:
                funcao()
                passou += 1
                print("  PASSOU   %s" % nome)
            except AssertionError as erro:
                msg = str(erro) or "a condicao do assert deu falso"
                falhou.append((nome, "assercao falhou: %s" % msg))
                print("  FALHOU   %s" % nome)
            except NotImplementedError as erro:
                falhou.append((nome, "codigo ainda nao implementado: %s" % erro))
                print("  VERMELHO %s" % nome)
            except Exception as erro:
                falhou.append((nome, "%s: %s" % (type(erro).__name__, erro)))
                print("  ERRO     %s" % nome)
    print("-" * 62)
    print("%d passaram, %d falharam" % (passou, len(falhou)))
    if falhou:
        print()
        print("Detalhe das falhas:")
        for nome, motivo in falhou:
            print("  %s" % nome)
            print("      %s" % motivo)
    if avisos:
        print()
        print("Avisos:")
        for aviso in avisos:
            print("  " + aviso)
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
