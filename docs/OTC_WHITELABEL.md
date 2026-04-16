# DOCUMENTAÇÃO: INFRAESTRUTURA WHITE LABEL OTC

Esta documentação detalha a implementação da camada White Label para mesas de negociação OTC (Over-The-Counter) integrada ao projeto **START-SE**.

---

## 1. Arquitetura Multi-tenant (Isolamento de Dados)

Foi implementada uma arquitetura de **Banco de Dados Compartilhado com Isolamento Lógico**. Isso permite gerenciar múltiplos clientes (donos de mesas) em uma única instância do Django.

### Componentes Core:
- **`core/multitenancy.py`**:
    - **Middleware**: Detecta automaticamente o tenant atual através do header `X-Tenant-ID` ou pelo subdomínio da URL (ex: `mesa-a.startse.com`).
    - **Context Storage**: Utiliza `threading.local` para garantir que o ID do tenant esteja acessível em qualquer lugar do código durante a requisição.
    - **TenantManager**: Um gerenciador de banco de dados que filtra automaticamente todas as consultas (`.all()`, `.filter()`) para que um tenant nunca veja os dados de outro.
    - **TenantBaseModel**: Classe base para modelos que precisam de isolamento. Adiciona automaticamente o campo `tenant_id`.

---

## 2. Modelagem de Dados (App `otc`)

O novo app `otc` contém a lógica central de negociação:

### Modelos Principais:
1. **`TenantProfile`**: Perfil da Mesa de Negociação.
    - Vinculado a um usuário (Dono da Mesa).
    - Configurações de branding (Logo, Cores).
    - **Spread Padrão**: Define a margem de lucro automática aplicada em cada cotação.
2. **`Quote` (RFQ)**: Registro de Solicitação de Cotação.
    - Armazena o preço base (mercado), o spread aplicado e o preço final.
    - Possui um tempo de expiração (Lock de preço) de 30 segundos.
3. **`Trade`**: Registro de operações executadas.
    - Vinculado a uma cotação aceita.
    - Armazena valores finais e volume para fins de liquidação.

---

## 3. Motor de Preços e RFQ (Request for Quote)

A lógica de precificação está centralizada em `otc/services.py`:

- **Motor de Preços (`PricingService`)**: 
    - Integrado com `yfinance` para buscar preços reais de ativos (ex: BTC-BRL).
    - Se falhar, possui fallback de segurança.
    - Calcula o `final_price` aplicando o spread configurado no `TenantProfile`.
- **RFQ Service (`RFQService`)**:
    - Gerencia a criação da cotação com preço travado.
    - Valida a expiração antes de permitir a execução do Trade.

---

## 4. Segurança e Painel Administrativo

O **Django Admin** foi customizado em `otc/admin.py` para garantir o isolamento total entre os donos das mesas:

- **Isolamento de Queryset**: Donos de mesa visualizam apenas seus próprios perfis, cotações e transações.
- **Auto-vínculo**: Ao criar um novo registro pelo admin, o sistema vincula automaticamente o `tenant_id` do usuário logado.
- **Superusuários**: Mantêm visão global de todos os tenants para fins de suporte e auditoria.

---

## 5. Endpoints de API

A infraestrutura está pronta para ser consumida via frontend ou integradores externos:

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| **POST** | `/otc/rfq/request/` | Solicita uma cotação travada por 30 segundos. |
| **POST** | `/otc/rfq/execute/` | Executa o trade baseado no `quote_id`. |

---

## 6. Próximos Passos Técnicos

> [!IMPORTANT]
> **Migrações Pendentes**: As tabelas foram definidas no código, mas precisam ser criadas no banco de dados.
> 1. Resolver o apontamento do `python` no ambiente local.
> 2. Rodar `python manage.py makemigrations otc` e `python manage.py migrate`.

---
**Documentação consolidada da infraestrutura OTC White Label.**
