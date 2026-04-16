# DOCUMENTAÇÃO DE TESTES: OTC CORE MICROSERVICE

Esta documentação detalha a suíte de testes automatizados implementada para o motor de negociação OTC, garantindo a integridade das regras de negócio e a resiliência da infraestrutura.

---

## 1. Estratégia de Testes

A suíte segue a pirâmide de testes focada no isolamento das camadas da **Clean Architecture**. Todos os testes estão localizados no diretório `otc-core-service/tests/`.

| Camada | Tipo de Teste | Alvo | Ferramentas |
| :--- | :--- | :--- | :--- |
| **Domínio** | Unitário | Entidades e Regras Puras | Pytest |
| **Aplicação** | Unitário (Mockado) | Casos de Uso (RFQ) | Pytest + Mock |
| **Infraestrutura** | Resiliência | Circuit Breaker | Pytest + Time |

---

## 2. Suítes de Teste em Detalhe

### A. Testes de Domínio (`tests/domain/`)
Focados na validade das entidades de negócio sem dependências externas.
- **`test_entities.py`**:
    - Valida se a lógica de expiração do `Quote` (`is_expired()`) funciona corretamente para tempos passados e futuros.
    - Garante que nenhuma negociação ocorra com cotações expiradas.

### B. Testes de Aplicação (`tests/application/`)
Focados na orquestração dos serviços e casos de uso.
- **`test_request_quote.py`**:
    - Utiliza **Mocks** para substituir o banco de dados (`IOTCRepository`), o provedor de preços (`IPriceProvider`) e o serviço de KYC (`IKYCService`).
    - **Cenários**:
        - **Sucesso**: Verifica se a cotação é criada com os valores corretos e persistida.
        - **Elegibilidade**: Garante que o sistema lance uma exceção se o serviço de KYC reprovar o usuário.

### C. Testes de Infraestrutura (`tests/infrastructure/`)
Focados na robustez e tratamento de falhas externas.
- **`test_circuit_breaker.py`**:
    - Simula falhas em série para validar a mudança de estado do circuito.
    - **Estados Testados**:
        - `CLOSED` -> `OPEN` (após atingir o limite de falhas).
        - `OPEN` (bloqueio imediato de novas chamadas).
        - `HALF-OPEN` -> `CLOSED` (recuperação após o timeout de segurança).

---

## 3. Como Executar os Testes

Para rodar os testes, é necessário ter o `pytest` instalado no ambiente Python.

```bash
# 1. Instalar dependências de teste
pip install pytest

# 2. Executar todos os testes
pytest otc-core-service/tests

# 3. Executar com relatório de verbose
pytest -v otc-core-service/tests
```

---

## 4. Manutenção e Boas Práticas

- **Independentes de Banco**: Estes testes não requerem um banco de dados real (PostgreSQL/SQLite), tornando-os extremamente rápidos.
- **Agnósticos de Versão**: Podem ser executados em qualquer versão do Python 3.10+ devido ao uso de tipos padrão e mocks nativos da linguagem.
- **Inclusão de Novos Testes**: Sempre que um novo Caso de Uso for criado em `application/use_cases/`, um arquivo correspondente deve ser criado em `tests/application/`.

---
**Documentação consolidada da suíte de testes do motor OTC.**
