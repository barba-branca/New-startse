# DOCUMENTAÇÃO TÉCNICA: MICROSERVIÇO OTC CORE

Esta documentação descreve a arquitetura e os padrões de implementação do **OTC Core Microservice**, projetado para alta performance, escalabilidade e conformidade com os princípios SOLID e Clean Architecture.

---

## 1. Visão Geral da Arquitetura

O microserviço segue a **Clean Architecture**, dividindo o código em camadas concêntricas onde a dependência aponta sempre para o centro (o Domínio).

### Estrutura de Camadas:
1.  **Domain (`src/domain/`)**: O coração do sistema. Contém a lógica de negócio pura, sem dependência de bancos de dados ou APIs externas.
2.  **Application (`src/application/`)**: Orquestra os fluxos de dados usando os **Casos de Uso (Use Cases)**.
3.  **Infrastructure (`src/infrastructure/`)**: Contém os adaptadores para ferramentas externas (Django ORM, Yahoo Finance, Circuit Breaker).
4.  **Interface (`src/interface/`)**: Pontos de entrada para o mundo exterior (API REST e Ferramentas MCP).

---

## 2. Princípios SOLID Aplicados

### Inversão de Dependência (DIP)
O Caso de Uso `RequestQuote` não sabe que o `yfinance` existe. Ele depende da interface `IPriceProvider`. Isso permite que você troque o provedor de liquidez no futuro alterando apenas uma linha na configuração de infraestrutura.

### Princípio da Responsabilidade Única (SRP)
- A validação de elegibilidade do usuário foi separada do motor de negociação (via `IKYCService`).
- O cálculo de spread foi isolado em uma estratégia (`ISpreadStrategy`).

---

## 3. Padrões de Projeto (Design Patterns)

### Strategy Pattern (Cálculo de Spread)
Implementado para permitir que diferentes donos de mesas (Tenants) tenham regras de negócio distintas.
- Arquivo: `src/domain/interfaces.py` -> `ISpreadStrategy`
- Implementação: `src/infrastructure/price_feeds/yahoo_adapter.py` -> `DefaultSpreadStrategy`

### Adapter Pattern (Integração Django)
Permite que o microserviço aproveite o poder do Django para persistência de dados sem se tornar "escravo" do framework.
- Local: `src/infrastructure/persistence/django_adapter.py`

### Circuit Breaker (Resiliência FinTech)
Proteção contra falhas em sistemas externos. Se o provedor de cotações falhar repetidamente, o circuito "abre", impedindo que o sistema fique travado aguardando timeouts e protegendo a experiência do usuário.
- Local: `src/infrastructure/circuit_breaker.py`

---

## 4. Integração com MCP (Model Context Protocol)

O microserviço foi projetado para ser consumido por agentes de IA de forma nativa.
- **Tools**: Estão definidas em `src/interface/api/controllers.py`, seguindo o esquema JSON-RPC do MCP.
- **Benefício**: Qualquer agente compatível com MCP pode agora solicitar cotações e verificar status de ordens de forma estruturada.

---

## 5. Como Estender o Microserviço

- **Novo Provedor de Preços**: Crie uma nova classe em `infrastructure/price_feeds/` que herde de `IPriceProvider`.
- **Novo Banco de Dados**: Se decidir mudar para MongoDB ou Redis, basta criar um novo adaptador em `infrastructure/persistence/` que implemente `IOTCRepository`.
- **Novo Caso de Uso**: Adicione em `application/use_cases/` (ex: `CancelOrderUseCase`).

---

> [!IMPORTANT]
> **Manutenibilidade**: Ao manter o Domínio isolado, você garante que sua lógica de negócio nunca se torne obsoleta devido a mudanças em bibliotecas de terceiros ou frameworks.

**Status da Implementação**: Estrutura Core, RFQ Flow, Resiliência e Adaptores Django concluídos.
