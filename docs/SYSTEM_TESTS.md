# Guia de Testes de Sistema (E2E)

Este documento descreve os cenários de teste de sistema e interface para a plataforma **New Start-se**, com foco nas validações visuais e de comportamento dinâmico.

## 1. Cenários de Teste

### SVT-01: Verificação de Rebranding Global
- **Objetivo**: Garantir que o nome "New Start-se" substituiu todas as instâncias antigas de "STARTSE".
- **Procedimento**:
    1. Acessar a Landing Page (`/`).
    2. Verificar tag `<title>`.
    3. Verificar Navbar (Brand text).
    4. Verificar Footer (Assinatura Develops Code).
- **Critério de Sucesso**: O nome "New Start-se" deve estar presente em todos os pontos de contato principais.

### SVT-02: Funcionamento do Ticker em Tempo Real
- **Objetivo**: Validar a busca e exibição dinâmica de preços.
- **Procedimento**:
    1. Abrir a página inicial.
    2. Aguardar a substituição do texto "CARREGANDO..." pelos dados.
    3. Verificar a presença de USD/BRL, BTC, ETH.
    4. Conferir as cores das variações (Verde para positivo, Vermelho para negativo).
- **Critério de Sucesso**: Dados injetados com sucesso sem erros de console (HTTP 200 nas APIs).

## 2. Relatório de Execução (SVT-01-02)

| Data | Teste | Status | Observações |
| :--- | :--- | :--- | :--- |
| 2026-04-16 | SVT-01 | **PASSOU** | Nome "New Start-se" validado em H1, Navbar e Footer. |
| 2026-04-16 | SVT-02 | **PASSOU** | Ticker operando via Binance/AwesomeAPI com rolagem fluida. |

## 3. Comandos para Teste Manual
Para verificar erros de JavaScript no navegador, utilize `F12 > Console`. Não devem existir erros de `CORS` ou `Mixed Content`.

---
**Documentação de qualidade e garantia de sistema.**
