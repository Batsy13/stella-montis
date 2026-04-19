# Interface Web (index.html)

**Caminho:** `app/templates/index.html`  
**Responsabilidade:** Interface do usuário. Gerencia a conexão WebSocket, permite capturar o CSS selector via Live Selector e controlar o monitoramento com start/stop.

---

## Visão Geral

A interface é uma página HTML single-page com design **glassmorphism**. Toda a lógica é em JavaScript vanilla com WebSocket nativo do browser. Não há iframe — a seleção de elementos ocorre em um browser Chromium separado aberto pelo backend.

---

## Layout

```
┌─────────────────────────────────────────────────────┐
│  ████ STELLA MONTIS                                  │
│  SISTEMA://ONLINE_                                   │
├─────────────────────────────────────────────────────┤
│  COORDENADA DE ORIGEM (URL):                        │
│  [https://www.target-site.com              ]        │
│  [ SINCRONIZAR INTERFACE DE CAPTURA ]               │
│                                                     │
│  VETOR DE DADOS (XPATH):                            │
│  [AGUARDANDO INPUT EXTERNO...    ] (readonly)       │
│                                                     │
│  [ INICIAR PROTOCOLO DE VIGÍLIA  ]                  │
│  [ INTERROMPER PROTOCOLO         ] (oculto)         │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  STATUS: PROTOCOLO INICIADO.                │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## Elementos HTML

| ID / Classe | Elemento | Função |
|---|---|---|
| `#url` | `<input type="text">` | URL da página a monitorar |
| `#xpath` | `<input readonly>` | CSS selector (preenchido via WebSocket) |
| `.btn-capture` | `<button>` | Dispara `startCapture()` → envia URL ao WebSocket |
| `.btn-start` | `<button>` | Dispara `startMonitoring()` → `POST /start` |
| `.btn-stop` | `<button>` (oculto) | Dispara `stopMonitoring()` → `POST /stop` |
| `#ws-indicator` | `<div>` | Indicador de status do WebSocket (ONLINE/OFFLINE) |
| `#feedback-ui` | `<div>` | Caixa de status com mensagem e cor por tipo |

---

## Conexão WebSocket

```javascript
const wsUrl = `${wsProtocol}//${window.location.host}/ws/xpath`;

function connectWS() {
    ws = new WebSocket(wsUrl);

    ws.onopen  = () => { indicator.textContent = "SISTEMA://ONLINE_"; }
    ws.onclose = () => {
        indicator.textContent = "SISTEMA://LINK_LOST_RECONNECTING...";
        setTimeout(connectWS, 3000);   // reconnect automático
    }
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "xpath_result") {
            document.getElementById("xpath").value = data.xpath;
            showStatus("Vetor capturado com sucesso.", "success");
        }
    };
}
connectWS();
```

A conexão é estabelecida ao carregar a página e **reconecta automaticamente** a cada 3 segundos em caso de queda.

---

## Funções JavaScript

### `startCapture()`

```javascript
function startCapture() {
    const url = document.getElementById("url").value;
    if (!url || !url.startsWith("http")) {
        showStatus("URL INVÁLIDA.", "error");
        return;
    }
    ws.send(JSON.stringify({ url }));
    showStatus("INTERFACE ABERTA. SELECIONE O ALVO.", "info", 10000);
}
```

Valida a URL e envia ao WebSocket. O backend abre o Chromium e aguarda o clique do usuário.

---

### `startMonitoring()`

```javascript
async function startMonitoring() {
    const url   = document.getElementById("url").value;
    const xpath = document.getElementById("xpath").value;

    const response = await fetch("/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, xpath }),
    });

    if (response.ok) {
        showStatus("PROTOCOLO INICIADO.", "success", 8000);
        document.querySelector('.btn-start').style.display = 'none';
        document.querySelector('.btn-stop').style.display  = 'block';
    }
}
```

Após sucesso, alterna a visibilidade dos botões: esconde "Iniciar" e exibe "Interromper".

---

### `stopMonitoring()`

```javascript
async function stopMonitoring() {
    const url = document.getElementById("url").value;

    const response = await fetch("/stop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
    });

    if (response.ok) {
        showStatus("PROTOCOLO INTERROMPIDO.", "info", 8000);
        document.querySelector('.btn-start').style.display = 'block';
        document.querySelector('.btn-stop').style.display  = 'none';
    }
}
```

---

### `showStatus(message, type, duration)`

Exibe uma mensagem na caixa `#feedback-ui` com estilo visual por tipo:

| Tipo | Cor da borda | Uso |
|---|---|---|
| `info` | Cyan (`--industrial-cyan`) | Ações em andamento |
| `success` | Verde (`--status-green`) | Confirmações |
| `error` | Vermelho (`#ff6b6b`) | Erros e validações |

Após `duration` ms (padrão 5000), a caixa é ocultada automaticamente.

---

## Design System

As variáveis CSS definem a identidade visual do projeto:

```css
:root {
    --snow-white:       #f0f4f7;
    --machinery-grey:   #2d3436;
    --industrial-cyan:  #00d2ff;
    --warning-orange:   #ff9f43;
    --status-green:     #00ff88;
    --border-glass:     rgba(255, 255, 255, 0.2);
}
```

O container usa `backdrop-filter: blur(12px)` com fundo semi-transparente, criando o efeito **glassmorphism**. Botões têm bordas retas (`border-radius: 0`) e texto em `text-transform: uppercase` — estética industrial.
