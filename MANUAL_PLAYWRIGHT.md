# Manual do Playwright - guia rapido da disciplina

Teste e Qualidade de Software - IFCE - Campus Caninde - 2026.2
Prof.a Jamile Martins

Este manual cobre o que voce precisa para a **Pratica 11**. Nao e a documentacao
oficial do Playwright: e o subconjunto que a nossa pagina exige, com os nomes e
os identificadores reais do nosso formulario.

---

## 1. O que o Playwright faz

Ele abre um navegador de verdade, sem janela visivel, e opera a pagina no seu
lugar: clica, digita, le o que apareceu. Serve para testar **a interface**, e nao
a funcao por dentro.

A diferenca em relacao ao que voces ja fizeram:

| Ate agora | Com Playwright |
|---|---|
| `validar_solicitacao(4, 48, "Lab 1")` | preencher o campo, clicar no botao, ler a tela |
| testa a funcao | testa o caminho que o usuario percorre |
| falha aponta a linha do defeito | falha aponta que a tela nao fez o que devia |

Um teste de interface e mais lento e mais fragil que um de unidade. Por isso a
piramide da Unidade V pede muitos testes de unidade e poucos de interface.

---

## 2. Como rodar

No terminal do Codespace, na raiz do repositorio:

```bash
pytest tests_ui -v
```

O `-v` mostra o nome de cada teste. Sem ele, voce ve so pontos.

Para rodar um arquivo so:

```bash
pytest tests_ui/test_exemplo_playwright.py -v
```

---

## 3. Anatomia de um teste de interface

Abra o `tests_ui/test_exemplo_playwright.py`. Ele tem tres partes.

### A fixture: abre o navegador uma vez

```python
@pytest.fixture(scope="module")
def pagina():
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        aba = navegador.new_page()
        yield aba
        navegador.close()
```

Nao mexa nela. O `scope="module"` faz o navegador abrir uma vez para o arquivo
inteiro, em vez de uma vez por teste - e e o que torna a suite rapida.

### A funcao auxiliar: faz o trabalho repetitivo

```python
def solicitar(aba, duracao, antecedencia, laboratorio):
    aba.goto(PAGINA)
    aba.fill("#duracao", str(duracao))
    aba.fill("#antecedencia", str(antecedencia))
    aba.fill("#laboratorio", laboratorio)
    aba.click("#enviar")
    return aba.inner_text("#resultado")
```

**Use esta funcao nos seus testes.** Ela ja esta pronta no arquivo. Cada teste
seu vira uma linha de chamada e uma de verificacao.

### O teste

```python
def test_alguma_coisa(pagina):
    texto = solicitar(pagina, 2, 48, "Lab 1")
    assert "sucesso" in texto
```

O parametro `pagina` nao e um valor que voce passa: e a fixture, que o pytest
injeta sozinho. **Esse e o unico parametro permitido** nas funcoes de teste
desta disciplina.

---

## 4. Os identificadores da nossa pagina

Para o Playwright achar um elemento, voce usa um seletor. Na nossa pagina todos
os elementos tem `id`, e o seletor de id comeca com `#`.

| Elemento | Seletor | Para que serve |
|---|---|---|
| Campo de duracao | `#duracao` | preencher as horas-aula |
| Campo de antecedencia | `#antecedencia` | preencher as horas de antecedencia |
| Campo de laboratorio | `#laboratorio` | preencher o nome do laboratorio |
| Botao | `#enviar` | enviar a solicitacao |
| Area de resposta | `#resultado` | ler o que o sistema respondeu |

Sao esses cinco. Nao ha outros.

---

## 5. As acoes

```python
aba.goto(PAGINA)                      # abre a pagina
aba.fill("#duracao", "4")             # apaga o conteudo e digita
aba.click("#enviar")                  # clica
texto = aba.inner_text("#resultado")  # le o texto visivel do elemento
titulo = aba.title()                  # le o titulo da aba
```

Repare que `fill` sempre recebe **texto**, mesmo para numero. Por isso o
`str(duracao)` na funcao auxiliar.

---

## 6. As verificacoes

O teste termina com `assert`. O que verificar depende do que a pagina mostra:

```python
assert "sucesso" in texto              # a resposta contem a palavra
assert "duracao_minima" in texto       # a resposta cita um erro especifico
assert texto != ""                     # houve alguma resposta
assert ("sucesso" in texto) is True    # forma explicita
```

A nossa pagina responde de duas maneiras:

- quando aceita: uma frase contendo a palavra **sucesso**
- quando recusa: uma frase contendo os codigos dos erros, separados por virgula

Entao, para afirmar que a pagina ACEITOU, procure `"sucesso" in texto`. Para
afirmar que RECUSOU, procure `"sucesso" not in texto`, ou procure o codigo do
erro que voce espera.

---

## 7. Erros comuns

| Mensagem | O que significa | O que fazer |
|---|---|---|
| `TimeoutError` ao esperar um seletor | o elemento nao existe com aquele id | confira a tabela da secao 4; `#duracao` com acento nao existe |
| `Target page, context or browser has been closed` | o navegador caiu, quase sempre por falta de biblioteca de sistema | rode `python -m playwright install --with-deps chromium` |
| `fixture 'pagina' not found` | o teste esta em outro arquivo, sem a fixture | mantenha os testes no mesmo arquivo da fixture, ou copie a fixture |
| `missing required positional argument` | a funcao de teste tem parametro demais | so `pagina` e permitido; um teste por caso |
| O teste passa mas nao deveria | o `assert` esta fraco | `assert texto` e verdadeiro para qualquer texto; verifique o conteudo |

---

## 8. Pedindo codigo de Playwright a uma IA

A IA escreve Playwright bem, desde que voce diga o formato. Sem isso ela vai
devolver algo que nao roda aqui. Inclua estas restricoes no seu prompt:

```
- use a funcao solicitar(aba, duracao, antecedencia, laboratorio) que ja existe
- use a fixture chamada pagina, com scope de modulo
- funcoes de teste comecam com test_ e recebem SOMENTE o parametro pagina
- nao use pytest.mark.parametrize
- um teste por caso, com nome descritivo
- nao invente seletores: use apenas #duracao, #antecedencia, #laboratorio,
  #enviar e #resultado
```

A restricao sobre `parametrize` e a mais importante: e o que a IA mais faz por
conta propria, e e o que mais quebra a execucao aqui.

---

## 9. Referencia rapida

```python
# cabecalho de um arquivo de teste de interface
import pathlib
import pytest
from playwright.sync_api import sync_playwright

PAGINA = (pathlib.Path(__file__).resolve().parent.parent
          / "web" / "agendamento.html").as_uri()

# um teste
def test_descricao_do_caso(pagina):
    texto = solicitar(pagina, 2, 48, "Lab 1")
    assert "sucesso" in texto
```

```bash
pytest tests_ui -v                    # roda todos
pytest tests_ui -v -k duracao         # roda so os que tem "duracao" no nome
pytest tests_ui -v -x                 # para no primeiro que falhar
```

---

## 10. Onde aprender mais

A documentacao oficial e boa e tem versao em portugues parcial:
<https://playwright.dev/python/docs/intro>

Para esta pratica, o que esta neste manual basta.
