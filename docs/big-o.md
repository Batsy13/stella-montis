# Análise de Complexidade — Big O

Esta página analisa a complexidade de tempo e espaço das principais funções do Stella Montis.

---

## Resumo Geral

| Função | Complexidade de Tempo | Complexidade de Espaço |
|---|---|---|
| `monitor_price()` | **O(n)** — linear no número de iterações | **O(1)** — constante |
| `send_email()` | **O(1)** — constante | **O(m)** — linear no tamanho da mensagem |
| `setup_logger()` | **O(1)** — constante | **O(1)** — constante |
| `proxy()` — remoção de tags | **O(k)** — linear no tamanho do HTML | **O(k)** — linear no tamanho do HTML |
| Cálculo do CSS selector (JS) | **O(d × s)** — profundidade DOM × siblings | **O(d)** — profundidade DOM |

---

## Análise Detalhada

---

### `monitor_price()` — O(n)

```python
async def monitor_price(url, selector, email, interval=10):
    last_value = None                  # O(1)

    await page.goto(url)               # O(1) — uma requisição HTTP

    while True:                        # loop infinito: n iterações
        locator = page.locator(...)    # O(1) — referência lazy
        current_value = inner_text()   # O(1) — leitura de um elemento

        if current_value != last_value: # O(1) — comparação de strings
            send_email(...)             # O(1) — constante por chamada
            last_value = current_value  # O(1)

        await asyncio.sleep(interval)   # O(1)
```

**Complexidade de Tempo: O(n)**

Onde `n` é o número de iterações do loop (ciclos de polling). Cada iteração executa um conjunto fixo de operações de custo constante O(1).

O loop é **potencialmente infinito**, mas finito em execução prática: termina quando o browser é fechado, a task é cancelada ou ocorre um erro.

**Complexidade de Espaço: O(1)**

O consumo de memória é constante — apenas `last_value` e `current_value` são mantidos na memória. Não há acumulação de histórico ou estrutura crescente.

!!! note "Por que não O(∞)?"
    A notação Big O descreve o **crescimento em relação a uma entrada**. Aqui, a "entrada" é o número de ciclos executados `n`. O fato de `n` ser indeterminado não muda que cada ciclo tem custo O(1), tornando o total O(n). Em sistemas de monitoramento contínuos, O(n) no tempo com O(1) no espaço é o padrão ideal.

---

### `send_email()` — O(1) tempo, O(m) espaço

```python
def send_email(to_email, subject, message_body, is_html=False):
    msg = MIMEMultipart("alternative")    # O(1)
    msg["Subject"] = subject              # O(1)
    msg["From"] = EmailConfig.USER        # O(1)
    msg["To"] = to_email                  # O(1)

    part = MIMEText(message_body, ...)    # O(m) — cópia da mensagem
    msg.attach(part)                      # O(1)

    with smtplib.SMTP(...) as server:
        server.starttls()                 # O(1)
        server.login(user, pass)          # O(1)
        server.send_message(msg)          # O(m) — transmissão da mensagem
```

**Complexidade de Tempo: O(1)**

O número de operações é fixo, independente do tamanho da entrada. A transmissão via rede tem latência variável, mas não é computação local — é I/O.

**Complexidade de Espaço: O(m)**

Onde `m` é o tamanho do `message_body`. O objeto `MIMEText` armazena uma cópia da mensagem na memória.

---

### `setup_logger()` — O(1)

```python
def setup_logger(log_level="INFO"):
    logger.remove()      # O(1)
    logger.add(stdout)   # O(1)
    logger.add(file)     # O(1)
```

**Complexidade de Tempo: O(1)** — número fixo de operações de configuração.  
**Complexidade de Espaço: O(1)** — adiciona dois handlers ao singleton do Loguru.

---

### `proxy()` — O(k) no tamanho do HTML

```python
async def proxy(url):
    html = await page.content()    # O(k) — k = tamanho do HTML

    # Remoção de tags via regex — percorre o HTML inteiro
    html = re.sub(r'<meta...CSP...>', '', html)   # O(k)
    html = re.sub(r'<meta...X-Frame...>', '', html) # O(k)
    html = re.sub(r'<script...>', '', html)         # O(k)

    # Substituição de strings — O(k)
    html = html.replace("<head>", f"<head>{base_tag}")
    html = html.replace("</body>", f"{script}</body>")

    return html    # O(k)
```

**Complexidade de Tempo: O(k)**

Onde `k` é o tamanho em caracteres do HTML da página. Cada operação `re.sub` e `replace` percorre o HTML uma vez — são 5 operações lineares, mas por ser fator constante: O(5k) = **O(k)**.

**Complexidade de Espaço: O(k)**

Cada `re.sub` pode criar uma nova string de tamanho próximo a `k`. O pico de memória é aproximadamente 2×k (string original + string resultante).

---

### Cálculo do CSS Selector (JavaScript) — O(d × s)

```javascript
while (el.nodeType === Node.ELEMENT_NODE) {      // O(d) iterações
    // Para cada nó na subida:
    let sib = el, nth = 1;
    while (sib = sib.previousElementSibling) {   // O(s) iterações
        if (sib.nodeName === selector) nth++;
    }
    path.unshift(selector + `:nth-of-type(${nth})`);
    el = el.parentNode;
}
```

**Complexidade de Tempo: O(d × s)**

Onde:
- `d` = profundidade do elemento na árvore DOM (normalmente 5–20 níveis)
- `s` = número máximo de siblings do mesmo tipo em qualquer nível

Na prática, para páginas típicas: d ≤ 20, s ≤ 50 → O(1000) ≈ **O(1)** para fins práticos.

**Complexidade de Espaço: O(d)**

O array `path` armazena um seletor por nível de profundidade.

---

## Comparação com Abordagens Alternativas

| Abordagem | Complexidade de Tempo | Complexidade de Espaço | Observação |
|---|---|---|---|
| **Polling (atual)** | O(n) | O(1) | Simples, sem estado acumulado |
| WebSocket nativo | O(n) | O(c) `c=conexões` | Mais eficiente para notificações em tempo real |
| Histórico de valores | O(n) | O(n) | Permitiria análise estatística, mas aumenta memória |
| Polling com batch | O(n) | O(b) `b=tamanho batch` | Reduziria chamadas SMTP agrupando notificações |

A escolha de polling com O(1) de espaço é adequada para o escopo do projeto: monitora **um** valor por instância de `monitor_price()`, sem necessidade de histórico.

---

## Conclusão

O sistema tem complexidade **linear no tempo (O(n))** e **constante no espaço (O(1))** para sua operação principal. Isso é o comportamento ótimo para um monitor de polling contínuo: cada ciclo é independente e não há acúmulo de estado ao longo do tempo.

A única operação com crescimento não-constante é o proxy (`O(k)`), mas é uma operação pontual (executada uma vez por URL carregada, não em loop).
