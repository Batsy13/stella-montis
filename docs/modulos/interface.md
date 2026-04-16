# Interface Web (index.html)

**Caminho:** `app/templates/index.html`  
**Responsabilidade:** Interface do usuário. Permite carregar qualquer URL em um iframe proxy e selecionar visualmente o elemento a monitorar.

---

## Visão Geral

A interface é uma página HTML single-page sem frameworks. Toda a lógica de interação está em JavaScript vanilla. O ponto central é o **iframe proxy**: a página alvo é carregada no backend via Playwright e re-servida pelo endpoint `/proxy`, com scripts de seleção visual injetados.

---

## Componentes da Interface

```
┌────────────────────────────────────────────────────────┐
│  Stella Montis                                         │
├────────────────────────────────────────────────────────┤
│  [URL: ___________________] [Email: _______________]   │
│  [Load Page]  [Start Monitoring]                       │
│  Carregando página, aguarde...                         │
│  Target XPath: <strong>None</strong>                   │
├────────────────────────────────────────────────────────┤
│                                                        │
│              iframe (70vh)                             │
│     página alvo renderizada com scripts injetados      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## Elementos HTML

| ID | Tipo | Função |
|---|---|---|
| `urlInput` | `<input type="text">` | URL da página a monitorar |
| `emailInput` | `<input type="email">` | E-mail para notificações |
| `loadUrl()` | `<button>` | Carrega a URL no iframe via proxy |
| `startBtn` | `<button>` | Aparece após seleção do elemento; dispara POST /start |
| `loading` | `<div>` | Spinner de texto exibido durante o carregamento |
| `xpathDisplay` | `<strong>` | Exibe o CSS selector do elemento selecionado |
| `proxyFrame` | `<iframe>` | Renderiza a página alvo processada pelo proxy |

---

## Funções JavaScript

### `loadUrl()`

```javascript
function loadUrl() {
    const url = document.getElementById('urlInput').value;
    if (url) {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('startBtn').style.display = 'none';
        proxyFrame.src = `/proxy?url=${encodeURIComponent(url)}`;
    }
}
```

- Exibe o indicador de carregamento
- Esconde o botão "Start Monitoring" (requer nova seleção após trocar de URL)
- Define o `src` do iframe para `/proxy?url=...`
- O iframe dispara `onload` quando o proxy responde, ocultando o indicador

---

### `window.addEventListener('message', ...)`

```javascript
window.addEventListener('message', function(event) {
    if (event.data && event.data.xpath) {
        currentXpath = event.data.xpath;
        document.getElementById('xpathDisplay').innerText = currentXpath;
        document.getElementById('startBtn').style.display = 'inline-block';
    }
});
```

Recebe o CSS selector enviado pelo script injetado no iframe via `postMessage`. Ao receber, exibe o selector na tela e habilita o botão "Start Monitoring".

---

### `startTask()`

```javascript
function startTask() {
    const url = document.getElementById('urlInput').value;
    const email = document.getElementById('emailInput').value;

    if (!email) {
        alert("Digite um e-mail!");
        return;
    }

    fetch('/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url, xpath: currentXpath, email: email })
    })
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => console.error(error));
}
```

Envia `POST /start` com `{ url, xpath, email }`. Exibe alerta de confirmação ao receber resposta.

---

## Comunicação entre Frames (postMessage)

O script injetado pelo proxy roda **dentro do iframe** (contexto isolado). Para enviar o selector para a página pai, usa a API `postMessage`:

```javascript
// Dentro do iframe (injetado pelo proxy):
window.parent.postMessage({ xpath: finalSelector }, '*');

// Na página pai (index.html):
window.addEventListener('message', function(event) {
    if (event.data && event.data.xpath) { ... }
});
```

!!! info "Por que postMessage?"
    Iframes com `sandbox="allow-scripts allow-same-origin"` têm acesso restrito ao DOM pai. O `postMessage` é o mecanismo padrão e seguro para comunicação entre frames de origens diferentes.

---

## Atributo `sandbox` do iframe

```html
<iframe id="proxyFrame" sandbox="allow-scripts allow-same-origin"></iframe>
```

| Flag | Efeito |
|---|---|
| `allow-scripts` | Permite execução de JavaScript (necessário para os scripts injetados) |
| `allow-same-origin` | Permite que o iframe acesse cookies e storage da mesma origem |

Flags **não incluídas** (comportamento de segurança):
- `allow-forms`: formulários desabilitados
- `allow-popups`: popups bloqueados
- `allow-top-navigation`: o iframe não pode redirecionar a página pai

---

## Cálculo do CSS Selector

O script injetado pelo proxy calcula o CSS selector do elemento clicado percorrendo a árvore DOM:

```javascript
let el = e.target;
let path = [];

while (el.nodeType === Node.ELEMENT_NODE) {
    let selector = el.nodeName.toLowerCase();
    if (el.id) {
        path.unshift('#' + el.id);
        break;  // ID é único, para aqui
    } else {
        let sib = el, nth = 1;
        while (sib = sib.previousElementSibling) {
            if (sib.nodeName.toLowerCase() === selector) nth++;
        }
        selector += `:nth-of-type(${nth})`;
    }
    path.unshift(selector);
    el = el.parentNode;
}

let finalSelector = path.join(' > ');
```

**Exemplo de selector gerado:**
```
#section-coin-overview > div:nth-of-type(2) > span:nth-of-type(1)
```

Se o elemento possui `id`, o algoritmo para no `#id` (mais curto e estável). Caso contrário, usa `:nth-of-type()` para diferenciar siblings.
