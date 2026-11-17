# -*- coding: utf-8 -*-
"""Analisador estático mínimo, em biblioteca padrão.

Uso:  python3 analisador.py reservas.py

Não substitui Ruff nem SonarLint: existe para que a prática funcione mesmo sem
internet no laboratório, e para mostrar que um linter é um programa que lê a
árvore sintática do código — não mágica.
"""

import ast
import sys

LIMITE_COMPLEXIDADE = 8
LIMITE_LINHAS = 25

RAMIFICA = (ast.If, ast.For, ast.While, ast.ExceptHandler,
            ast.With, ast.Assert, ast.comprehension)


def complexidade(func):
    """Complexidade ciclomática: 1 + número de pontos de decisão."""
    total = 1
    for no in ast.walk(func):
        if isinstance(no, RAMIFICA):
            total += 1
        elif isinstance(no, ast.BoolOp):
            total += len(no.values) - 1
    return total


def achados_de(arvore, fonte):
    achados = []
    linhas = fonte.splitlines()

    importados, usados = {}, set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for a in no.names:
                importados[(a.asname or a.name).split('.')[0]] = no.lineno
        elif isinstance(no, ast.ImportFrom):
            for a in no.names:
                importados[a.asname or a.name] = no.lineno
        elif isinstance(no, ast.Name):
            usados.add(no.id)
        elif isinstance(no, ast.Attribute):
            alvo = no
            while isinstance(alvo, ast.Attribute):
                alvo = alvo.value
            if isinstance(alvo, ast.Name):
                usados.add(alvo.id)
    for nome, ln in sorted(importados.items(), key=lambda x: x[1]):
        if nome not in usados:
            achados.append((ln, 'IMPORTE-NAO-USADO',
                            'o módulo "%s" é importado e nunca utilizado' % nome))

    for func in [n for n in ast.walk(arvore)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        c = complexidade(func)
        if c > LIMITE_COMPLEXIDADE:
            achados.append((func.lineno, 'COMPLEXIDADE-ALTA',
                            'a função "%s" tem complexidade ciclomática %d, acima do limite de %d'
                            % (func.name, c, LIMITE_COMPLEXIDADE)))
        n_linhas = (func.end_lineno or func.lineno) - func.lineno + 1
        if n_linhas > LIMITE_LINHAS:
            achados.append((func.lineno, 'FUNCAO-LONGA',
                            'a função "%s" tem %d linhas, acima do limite de %d'
                            % (func.name, n_linhas, LIMITE_LINHAS)))
        for d in func.args.defaults:
            if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                achados.append((func.lineno, 'DEFAULT-MUTAVEL',
                                'a função "%s" usa valor padrão mutável, compartilhado entre chamadas'
                                % func.name))
        retornos = [r for r in ast.walk(func) if isinstance(r, ast.Return)]
        tipos = set()
        for r in retornos:
            if r.value is None:
                tipos.add('nada')
            elif isinstance(r.value, ast.Constant) and r.value.value is None:
                tipos.add('None')
            elif isinstance(r.value, ast.Constant) and isinstance(r.value.value, bool):
                tipos.add('bool')
            else:
                tipos.add('valor')
        if len(tipos) > 1:
            achados.append((func.lineno, 'RETORNO-INCONSISTENTE',
                            'a função "%s" retorna tipos diferentes conforme o caminho: %s'
                            % (func.name, ', '.join(sorted(tipos)))))
        atribuidos = {}
        for no in ast.walk(func):
            if isinstance(no, ast.Name) and isinstance(no.ctx, ast.Store):
                atribuidos.setdefault(no.id, no.lineno)
        lidos = {n.id for n in ast.walk(func)
                 if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        for nome, ln in sorted(atribuidos.items(), key=lambda x: x[1]):
            if nome not in lidos:
                achados.append((ln, 'VARIAVEL-NAO-USADA',
                                'a variável "%s" é atribuída e nunca lida' % nome))

    for no in ast.walk(arvore):
        if isinstance(no, ast.ExceptHandler):
            corpo = [c for c in no.body if not isinstance(c, ast.Pass)]
            if not corpo:
                achados.append((no.lineno, 'EXCECAO-SILENCIADA',
                                'bloco except que descarta a exceção sem tratar nem registrar'))

    for i, linha in enumerate(linhas, start=1):
        if len(linha) > 100:
            achados.append((i, 'LINHA-LONGA', 'linha com %d caracteres' % len(linha)))

    return sorted(achados)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    caminho = sys.argv[1]
    with open(caminho, encoding='utf-8') as f:
        fonte = f.read()
    achados = achados_de(ast.parse(fonte), fonte)
    print('Analisando %s' % caminho)
    print('-' * 78)
    for ln, regra, msg in achados:
        print('%s:%-4d %-22s %s' % (caminho, ln, regra, msg))
    print('-' * 78)
    print('%d achado(s).' % len(achados))


if __name__ == '__main__':
    main()
