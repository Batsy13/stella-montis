# Análise de Complexidade — Big O

---

## Resumo Geral

| Função | Complexidade de Tempo | Complexidade de Espaço |
|---|---|---|
| `monitor_price()` | **O(n)** — linear no número de iterações | **O(1)** — constante |
| `send_google_form()` | **O(1)** — constante | **O(m)** — tamanho da mensagem |
| `show_visual_form()` | **O(1)** — constante | **O(1)** — constante |
| `open_live_selector()` | **O(t)** — linear no tempo aberto | **O(d)** — profundidade DOM |
| `setup_logger()` | **O(1)** — constante | **O(1)** — constante |
| Cálculo do CSS selector (JS) | **O(d × s)** — profundidade × siblings | **O(d)** — profundidade DOM |

---

## Análise Detalhada

---

### `monitor_price()` — O(n) tempo, O(1) espaço

```python
async def monitor_price(url, selector, interval=10):
    last_value = None                        # O(1)
    await page.goto(url)                     # O(1) — uma requisição

    while True:                              # n iterações
        locator = page.locator(selector)     # O(1) — referência lazy
        current_value = inner_text().strip() # O(1) — leitura de um elemento
        if current_value != last_value:      # O(1) — comparação de strings
            show_visual_form(message)        # O(1) por chamada
            last_value = current_value       # O(1)
        await asyncio.sleep(interval)        # O(1)
```

**Tempo: O(n)** — onde `n` é o número de ciclos de polling. Cada iteração tem custo fixo O(1).

**Espaço: O(1)** — apenas `last_value` e `current_value` em memória. Sem acúmulo histórico.

!!! note "Loop infinito vs. O(n)"
    Big O descreve crescimento em relação à entrada. A entrada aqui é `n` = número de iterações. O fato de ser potencialmente infinito não muda que cada iteração custa O(1). O(n) com O(1) de espaço é o comportamento ideal para um monitor de polling contínuo.

---

### `send_google_form()` — O(1) tempo, O(m) espaço

```python
def send_google_form(message):
    requests.post(GOOGLE_FORM_URL, data={"entry...": message})  # O(1)
```

**Tempo: O(1)** — número fixo de operações independente da entrada. A latência de rede é I/O, não computação.

**Espaço: O(m)** — onde `m` é o tamanho de `message`. O `requests.post` serializa o corpo da requisição em memória.

---

### `show_visual_form()` — O(1) tempo, O(1) espaço

```python
async def show_visual_form(message):
    await page.goto(GOOGLE_FORM_VIEW)      # O(1)
    await page.fill('textarea', message)   # O(1)
    await page.locator('text=Enviar').click() # O(1)
```

**Tempo: O(1)** — número fixo de interações com o browser, independente da mensagem.

**Espaço: O(1)** — sem estruturas crescentes.

---

### `open_live_selector()` — O(t) tempo, O(d) espaço

```python
async def open_live_selector(url, websocket):
    await page.goto(url)             # O(1)
    while browser.is_connected():    # t iterações (1 por segundo)
        await asyncio.sleep(1)       # O(1)
```

**Tempo: O(t)** — onde `t` é o tempo em segundos que o browser fica aberto. Cada iteração do loop de espera é O(1).

**Espaço: O(d)** — o array `path` no script JavaScript cresce proporcionalmente à profundidade `d` do elemento clicado na árvore DOM.

---

### Cálculo do CSS Selector (JavaScript) — O(d × s)

```javascript
while (el.nodeType === Node.ELEMENT_NODE) {  // d iterações
    let sib = el, nth = 1;
    while (sib = sib.previousElementSibling) { // s iterações
        if (sib.nodeName === selector) nth++;
    }
    path.unshift(selector + `:nth-of-type(${nth})`);
    el = el.parentNode;
}
```

**Tempo: O(d × s)**  
- `d` = profundidade do elemento no DOM (tipicamente 5–20)
- `s` = número máximo de siblings do mesmo tipo em qualquer nível (tipicamente < 50)

Na prática: d ≤ 20, s ≤ 50 → ≈ 1000 operações — efetivamente **O(1)** para fins práticos.

**Espaço: O(d)** — array `path` com um seletor por nível.

---

## Comparação com Abordagens Alternativas

| Abordagem | Tempo | Espaço | Observação |
|---|---|---|---|
| **Polling atual** | O(n) | O(1) | Simples, sem estado acumulado |
| WebSocket push (servidor notifica) | O(1) por evento | O(c) conexões | Mais eficiente; exigiria controle sobre o site monitorado |
| Histórico de valores | O(n) | O(n) | Permitiria análise estatística ao custo de memória crescente |
| Polling com batch de notificações | O(n) | O(b) batch | Reduziria chamadas ao Google Forms agrupando mudanças |

A escolha de O(n) tempo / O(1) espaço é adequada ao escopo: uma instância de `monitor_price()` por URL, sem necessidade de histórico.

---

## Conclusão

A operação principal do sistema — `monitor_price()` — tem complexidade **O(n) no tempo e O(1) no espaço**, que é o comportamento ótimo para um monitor de polling contínuo: cada ciclo é independente e não há acúmulo de estado ao longo do tempo.

As funções auxiliares (`send_google_form`, `show_visual_form`) são O(1) no tempo — o custo não cresce com o número de chamadas. O único crescimento linear auxiliar é `open_live_selector()`, que é O(t) no tempo de uso do Live Selector — pontual e finito por natureza.
