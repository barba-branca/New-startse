# Documentação Técnica: Real-time Currency Ticker

Esta seção detalha a implementação do ticker financeiro em tempo real integrado à interface da **New Start-se**.

## 1. Motivação
A implementação original via backend (`yfinance`) apresentava instabilidades significativas em ambientes Windows devido a restrições de carregamento de DLLs e conflitos de threading com o servidor de desenvolvimento do Django. A migração para uma solução Client-side (JavaScript) garante:
- **Resiliência**: O servidor não trava se a API de preços falhar.
- **Performance**: Redução do tempo de resposta inicial da Landing Page (TTFB).
- **Tempo Real**: Cotações atualizadas dinamicamente sem recarregar a página.

## 2. Arquitetura de Dados

O componente consome dados de duas APIs públicas robustas:

| Fonte | Dados Obtidos | Endpoint |
| :--- | :--- | :--- |
| **Binance API** | BTC, ETH, SOL, BNB | `https://api.binance.com/api/v3/ticker/24hr` |
| **AwesomeAPI** | USD/BRL | `https://economia.awesomeapi.com.br/last/USD-BRL` |

## 3. Implementação Técnica

### Localização
O código reside inteiramente no arquivo `landingPage/templates/index.html`.

### Estrutura HTML
```html
<div class="ticker-wrap">
    <div class="ticker" id="crypto-ticker">
        <!-- Injetado via JS -->
    </div>
</div>
```

### Lógica JavaScript (`updateTicker`)
A função é executada imediatamente após o carregamento da página e em intervalos de **60 segundos**.
1. Realiza requisições assíncronas (`fetch`) para Binance e AwesomeAPI.
2. Formata os valores monetários (Locale de moeda).
3. Calcula a variação percentual (Up/Down) e altera a classe CSS para feedback visual (Verde/Vermelho).
4. Duplica o conteúdo injetado para criar um loop de animação infinito e sem emendas.

## 4. Estilização e Animação
A animação é controlada via CSS puro:
- **Keyframes `ticker`**: Move o contêiner de `0%` a `-100%` da largura.
- **Performance**: Utiliza `translate3d` para acionar a aceleração de hardware (GPU), garantindo 60fps na rolagem mesmo em dispositivos móveis.

---
**Documentação técnica de engenharia de interface.**
