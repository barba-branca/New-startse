# DOCUMENTAÇÃO: ESTRATÉGIA DE TESTES OTC CORE

Esta documentação detalha a suíte de testes automatizados implementada para o **OTC Core Microservice**, garantindo a integridade financeira e a resiliência operacional da plataforma.

---

## 1. Filosofia de Testes

Seguimos a abordagem de **Testes em Camadas (Clean Testing)**, onde cada nível foca em uma responsabilidade específica da arquitetura:

- **Isolamento**: Utilizamos Mocks para garantir que os testes de lógica de negócio não dependam de sistemas externos (Banco de Dados, Internet).
- **Rapidez**: Os testes são executados inteiramente em memória, permitindo feedback instantâneo.
- **Resiliência**: Focamos não apenas no "caminho feliz", mas também no comportamento do sistema sob estresse ou falha de provedores.

---

## 2. Cobertura da Suíte de Testes

### Camada 1: Domínio (Lógica Pura)
Local: `otc-core-service/tests/domain/`
- **Validação de Expiração**: Garante que o sistema identifique corretamente cotações fora do TTL (Time-To-Live) de 30 segundos.
- **Integridade de Dados**: Verifica se as entidades `Quote` e `Trade` mantêm seu estado consistente.

### Camada 2: Aplicação (Casos de Uso)
Local: `otc-core-service/tests/application/`
- **Fluxo RFQ (Request for Quote)**: Testa a orquestração entre o provedor de preços e o repositório.
- **Barreiras de Segurança (KYC)**: Valida se o sistema impede operações de usuários bloqueados ou não elegíveis.
- **Mocks Utilizados**: `IPriceProvider`, `IOTCRepository`, `IKYCService`.

### Camada 3: Infraestrutura (Resiliência)
Local: `otc-core-service/tests/infrastructure/`
- **Circular Breaker (Disjuntor)**: Testamos os estados `CLOSED`, `OPEN` e `HALF-OPEN`.
- **Prevenção de Cascata**: Garante que, se o provedor de liquidez falhar, o sistema pare de tentar requisições inúteis e proteja os recursos.

---

## 3. Instruções de Execução

Requisitos: `pytest`.

### Executar todos os testes:
```bash
pytest otc-core-service/tests
```

### Executar testes com relatório de verbosidade:
```bash
pytest -v otc-core-service/tests
```

### Executar apenas testes de resiliência:
```bash
pytest otc-core-service/tests/infrastructure/
```

---

## 4. Próximos Passos Sugeridos

1.  **Testes de Integração de Banco**: Implementar testes que validem o `DjangoOTCRepository` com um banco de dados de teste (SQLite in-memory).
2.  **Testes de Carga**: Simular 100+ RFQs simultâneos para medir o comportamento do Motor de Preços sob latência.

---
**Documentação consolidada da estratégia de testes para o motor OTC.**
