# Teste e Qualidade de Software - ambiente da disciplina

IFCE - Campus Caninde · Tecnologia em Analise e Desenvolvimento de Sistemas
Prof.a Jamile Martins · 2026.2

Este repositorio roda no **GitHub Codespaces**, direto no navegador: nao e
preciso instalar nada no computador do laboratorio nem ter permissao de
administrador.

Ele e usado na **Pratica 11, de 23/11**, que e a unica que depende do Playwright.
As praticas anteriores rodam com ferramentas de biblioteca padrao e nao precisam
deste ambiente - mas os arquivos delas estao aqui para consulta.

---

## Como abrir

1. Entre neste repositorio com a sua conta GitHub.
2. Clique no botao verde **Code**.
3. Escolha a aba **Codespaces** e depois **Create codespace on main**.
4. Espere montar. Na primeira vez demora alguns minutos, porque o ambiente
   instala as ferramentas e baixa o navegador usado pelo Playwright.

Quando terminar, voce vera o VS Code dentro do navegador, com um terminal.

## Como conferir se esta funcionando

```bash
python verificar_ambiente.py
```

O verificador roda todas as checagens e termina com um veredito. Se der
`ambiente pronto para a pratica`, pode comecar.

Se preferir conferir so a parte de interface:

```bash
pytest tests_ui -v
```

Deve passar **1 teste**: o exemplo que abre a pagina e confirma que ela responde.

## O que tem aqui

| Arquivo | Para que serve |
|---|---|
| `web/agendamento.html` | formulario de reserva - e o alvo dos testes de interface |
| `tests_ui/test_exemplo_playwright.py` | exemplo minimo: mostra a forma de um teste de interface |
| `solicitacao.py` | modulo-alvo das Praticas 07 e 08 |
| `reserva.py` | modulo do kata de TDD, Pratica 09 |
| `mutantes.py` | analisador de mutantes da disciplina |
| `rodar.py` | executor de testes da disciplina |
| `verificar_ambiente.py` | confere se o ambiente esta pronto |
| `reservas.py`, `analisador.py` | material da Pratica 04; ficam como historico |

O exemplo de interface **nao testa as regras de negocio**. Derivar os casos que
testam os requisitos e o trabalho da Pratica 11.

## Comandos usados nas praticas

```bash
# Praticas 07 e 08 - cobertura e escore de mutacao
python -m coverage run --branch -m pytest -q test_solicitacao_exemplo.py
python -m coverage report -m --include=solicitacao.py
python mutantes.py solicitacao.py test_solicitacao_exemplo.py

# Pratica 09 - kata de TDD
python rodar.py test_reserva.py

# Pratica 11 - interface com Playwright
pytest tests_ui -v
```

## Cota de uso

A conta gratuita inclui cerca de **60 horas por mes** na maquina basica, e as
praticas duram de 40 a 90 minutos. Duas recomendacoes:

- **Pare o Codespace ao terminar a aula**: menu inferior esquerdo, em
  *Codespaces* -> **Stop Current Codespace**. Ele hiberna e para de consumir tempo.
- Solicite o **GitHub Student Developer Pack** com o e-mail institucional, em
  <https://education.github.com/pack>. A verificacao leva alguns dias e dobra a
  cota - quem for pedir, peca agora.

Se a cota acabar, o acesso e bloqueado ate o mes seguinte. **Nao ha cobranca**,
desde que voce nao cadastre cartao.

## Se algo der errado

- **O Codespace nao abre:** confira se esta com a conta GitHub logada.
- **`pytest` nao e encontrado:** o ambiente ainda esta montando. Espere a
  mensagem de conclusao no terminal e tente de novo.
- **Erro de biblioteca ao abrir o navegador**, algo com `libX...so`: rode
  `python -m playwright install --with-deps chromium`.
- **Perdi meu trabalho:** use `git add`, `git commit` e `git push` ao fim de cada
  aula. O Codespace hiberna, mas nao e lugar seguro para trabalho nao versionado.
