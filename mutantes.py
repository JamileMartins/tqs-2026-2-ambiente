# -*- coding: utf-8 -*-
"""Analisador de mutantes da disciplina - biblioteca padrao, sem instalar nada.

Teste e Qualidade de Software - IFCE Campus Caninde - 2026.2

Gera mutantes do modulo alvo aplicando um operador de cada vez, executa a suite
de testes contra cada mutante e informa quais sobreviveram.

Uso:
    python mutantes.py                      alvo e suite padrao
    python mutantes.py solicitacao.py test_solicitacao_exemplo.py test_outro.py
    python mutantes.py --mostrar 7          mostra a alteracao do mutante 7
"""
import ast
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

# Sem argumentos, procura o alvo da pratica que estiver na pasta.
CANDIDATOS = [("reserva.py", ["test_reserva.py"]),
              ("solicitacao.py", ["test_solicitacao_exemplo.py"])]


def padroes():
    """Descobre o alvo e a suite a partir dos arquivos presentes na pasta."""
    import os
    for alvo, suites in CANDIDATOS:
        if os.path.exists(alvo):
            presentes = [s for s in suites if os.path.exists(s)]
            extras = sorted(f for f in os.listdir(".")
                            if f.startswith("test_") and f.endswith(".py")
                            and f not in presentes)
            return alvo, (presentes + extras) or suites
    return CANDIDATOS[0][0], CANDIDATOS[0][1]

_erros.exige_python_39()


# ----------------------------------------------------------------- operadores
TROCA_COMPARACAO = {
    ast.Lt: [ast.LtE, ast.Gt], ast.LtE: [ast.Lt, ast.GtE],
    ast.Gt: [ast.GtE, ast.Lt], ast.GtE: [ast.Gt, ast.LtE],
    ast.Eq: [ast.NotEq], ast.NotEq: [ast.Eq],
}
NOME_OP = {ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=",
           ast.Eq: "==", ast.NotEq: "!="}


class Ponto:
    """Um local do codigo onde cabe uma mutacao."""
    def __init__(self, operador, no, campo, novo, descricao, linha):
        self.operador = operador   # nome do operador de mutacao
        self.no = no               # no da arvore a ser alterado
        self.campo = campo         # (atributo, indice) a alterar
        self.novo = novo           # valor ou classe que substitui
        self.descricao = descricao
        self.linha = linha


def localizar(arvore):
    """Percorre a arvore e devolve a lista de mutacoes possiveis."""
    pontos = []
    for no in ast.walk(arvore):
        # operador relacional:  if x < 1  ->  if x <= 1
        if isinstance(no, ast.Compare):
            for i, op in enumerate(no.ops):
                for alternativo in TROCA_COMPARACAO.get(type(op), []):
                    pontos.append(Ponto(
                        "RELACIONAL", no, ("ops", i), alternativo,
                        "%s  ->  %s" % (NOME_OP[type(op)], NOME_OP[alternativo]),
                        getattr(no, "lineno", 0)))
        # constante numerica:  1  ->  2  e  1  ->  0
        if isinstance(no, ast.Constant) and isinstance(no.value, int) \
                and not isinstance(no.value, bool):
            for delta in (1, -1):
                pontos.append(Ponto(
                    "CONSTANTE", no, ("value", None), no.value + delta,
                    "%d  ->  %d" % (no.value, no.value + delta),
                    getattr(no, "lineno", 0)))
        # valor de retorno booleano:  return True  ->  return False
        if isinstance(no, ast.Constant) and isinstance(no.value, bool):
            pontos.append(Ponto(
                "BOOLEANO", no, ("value", None), not no.value,
                "%s  ->  %s" % (no.value, not no.value),
                getattr(no, "lineno", 0)))
        # operador logico:  and  ->  or
        if isinstance(no, ast.BoolOp):
            alternativo = ast.Or if isinstance(no.op, ast.And) else ast.And
            pontos.append(Ponto(
                "LOGICO", no, ("op", None), alternativo,
                "and  ->  or" if isinstance(no.op, ast.And) else "or  ->  and",
                getattr(no, "lineno", 0)))
    return pontos


def aplicar(fonte, indice_alvo):
    """Devolve o codigo-fonte com a mutacao de indice `indice_alvo` aplicada."""
    arvore = ast.parse(fonte)
    pontos = localizar(arvore)
    ponto = pontos[indice_alvo]
    campo, i = ponto.campo
    if campo == "ops":
        ponto.no.ops[i] = ponto.novo()
    elif campo == "op":
        ponto.no.op = ponto.novo()
    else:
        ponto.no.value = ponto.novo
    ast.fix_missing_locations(arvore)
    return ast.unparse(arvore), ponto


def _pede_parametro(funcao):
    """Diz se a funcao exige argumentos - caso tipico de pytest.mark.parametrize."""
    try:
        parametros = inspect.signature(funcao).parameters.values()
    except (TypeError, ValueError):
        return False
    return any(p.default is inspect.Parameter.empty
               and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
               for p in parametros)


def carregar_modulo(nome, fonte):
    modulo = types.ModuleType(nome)
    modulo.__file__ = nome + ".py"
    exec(compile(fonte, nome + ".py", "exec"), modulo.__dict__)
    return modulo


def rodar_suite(nome_alvo, fonte_alvo, suites, detalhar=False):
    """Executa as suites contra o modulo dado.

    Devolve True se TODAS passarem. Com detalhar=True, devolve (ok, motivo).
    """
    anterior = sys.modules.get(nome_alvo)
    sys.modules[nome_alvo] = carregar_modulo(nome_alvo, fonte_alvo)
    try:
        for caminho in suites:
            nome = caminho[:-3] if caminho.endswith(".py") else caminho
            sys.modules.pop(nome, None)
            with open(caminho, encoding="utf-8") as fp:
                fonte = fp.read()
            try:
                modulo = carregar_modulo(nome, fonte)
            except Exception as erro:
                return (False, _erros.explicar(erro, caminho)) if detalhar else False
            for atributo in sorted(vars(modulo)):
                if not atributo.startswith("test"):
                    continue
                funcao = getattr(modulo, atributo)
                if not callable(funcao):
                    continue
                if _pede_parametro(funcao):
                    motivo = (
                        "a funcao %s, de %s, recebe parametros.\n"
                        "   As ferramentas da disciplina executam funcoes de teste SEM\n"
                        "   parametros. Se o codigo veio de uma IA, ela provavelmente usou\n"
                        "   @pytest.mark.parametrize: peca um teste por caso, sem pytest."
                        % (atributo, caminho))
                    return (False, motivo) if detalhar else False
                try:
                    funcao()
                except Exception as erro:
                    motivo = ("o teste %s, de %s, falhou com %s: %s"
                              % (atributo, caminho, type(erro).__name__, erro))
                    return (False, motivo) if detalhar else False
        return (True, "") if detalhar else True
    finally:
        if anterior is not None:
            sys.modules[nome_alvo] = anterior
        else:
            sys.modules.pop(nome_alvo, None)


def main(argv):
    if "--ajuda" in argv or "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    mostrar = None
    if "--mostrar" in argv:
        i = argv.index("--mostrar")
        mostrar = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    alvo_auto, suites_auto = padroes()
    alvo = argv[0] if argv else alvo_auto
    suites = argv[1:] if len(argv) > 1 else suites_auto
    nome_alvo = alvo[:-3] if alvo.endswith(".py") else alvo

    try:
        with open(alvo, encoding="utf-8") as fp:
            original = fp.read()
        base = ast.unparse(ast.parse(original))
    except Exception as erro:
        print("ERRO: " + _erros.explicar(erro, alvo))
        return 1
    for suite in suites:
        import os as _os
        if not _os.path.exists(suite):
            print("ERRO: " + _erros.explicar(FileNotFoundError(), suite))
            return 1
    total = len(localizar(ast.parse(original)))

    if mostrar is not None:
        fonte, ponto = aplicar(original, mostrar - 1)
        print("Mutante %d | operador %s | linha %d"
              % (mostrar, ponto.operador, ponto.linha))
        print("Alteracao: %s" % ponto.descricao)
        print()
        print("Codigo do mutante:")
        print(fonte)
        return 0

    print("Analisador de mutantes - IFCE Campus Caninde")
    print("Alvo: %s   Suites: %s" % (alvo, ", ".join(suites)))
    print("-" * 68)

    ok, motivo = rodar_suite(nome_alvo, original, suites, detalhar=True)
    if not ok:
        print("ERRO: a suite nao passa no codigo ORIGINAL, entao nao da para medir nada.")
        print("   %s" % motivo)
        print("   Rode  python rodar.py  e deixe todos os testes verdes antes de medir.")
        return 1

    mortos, vivos = 0, []
    for i in range(total):
        fonte, ponto = aplicar(original, i)
        if fonte == base:
            continue
        passou = rodar_suite(nome_alvo, fonte, suites)
        if passou:
            vivos.append((i + 1, ponto))
            marca = "SOBREVIVEU"
        else:
            mortos += 1
            marca = "morto"
        print("  #%-3d  %-11s  linha %-3d  %-22s  %s"
              % (i + 1, ponto.operador, ponto.linha, ponto.descricao, marca))

    print("-" * 68)
    print("Mutantes gerados ....... %d" % total)
    print("Mortos ................. %d" % mortos)
    print("Sobreviventes .......... %d" % len(vivos))
    escore = (mortos / total * 100) if total else 0.0
    print("ESCORE DE MUTACAO ...... %.1f%%" % escore)
    if vivos:
        print()
        print("Sobreviventes a investigar:")
        for numero, ponto in vivos:
            print("  #%-3d  linha %-3d  %s" % (numero, ponto.linha, ponto.descricao))
        print()
        print("Use  python mutantes.py --mostrar N  para ver um mutante especifico.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
