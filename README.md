# 🚀 START-SE: Infraestrutura White Label OTC

A **START-SE** evoluiu de uma plataforma de crowdfunding para uma **infraestrutura White Label de ponta para mesas de negociação OTC (Over-The-Counter)**. Projetada para alta performance, ela combina o poder do Django com uma arquitetura de microsserviços limpa (Clean Architecture), garantindo escalabilidade e isolamento total entre diferentes operadoras (Desks).

---

## 🌟 Visão Geral

A plataforma permite que donos de mesas (Tenants) operem suas próprias marcas de negociação OTC com:
- **Isolamento de Dados Multi-tenant**: Garantia de privacidade e segurança entre mesas de negociação.
- **Motor de Preços RFQ (Request for Quote)**: Cotações em tempo real com travas de preço (TTL) e spreads dinâmicos.
- **Integração com IA Autônoma (S.A.K.A)**: Agentes inteligentes que automatizam análise de documentos e suporte ao investidor.

---

## 🏗️ Arquitetura do Sistema

O projeto utiliza uma abordagem híbrida moderna:

1.  **Monólito Central (Django)**: Gerencia usuários, Landing Pages e integrações legadas.
2.  **OTC Core Microservice**: Um serviço agnóstico construído seguindo **Clean Architecture** e **SOLID**, focado exclusivamente no motor de negociação e resiliência financeira.

### Camadas do Microserviço:
- **Domain**: Entidades e regras de negócio puras.
- **Application**: Casos de uso orquestrados (RFQ, Execução de Ordens).
- **Infrastructure**: Adaptadores robustos (Django ORM, Yahoo Finance, Circuit Breaker).
- **Interface**: Entrypoints amigáveis a **MCP (Model Context Protocol)** e APIs REST.

---

## 🛠️ Tecnologias Principais

- **Backend**: Django 5.1 & Python 3.14+
- **Arquitetura**: Clean Architecture / Microsserviços
- **Integrações de Preço**: Yahoo Finance (Integrated via Adapter)
- **IA/Agentes**: CrewAI & Framework S.A.K.A (C.A.S.A - Sistema de Agentes Autónomos)
- **Conformidade**: SOLID, Clean Code e Protocolo MCP

---

## 📚 Documentação Técnica

Para detalhes aprofundados, consulte nossa pasta **[`docs/`](/docs)**:

- 📑 **[Guia White Label OTC](/docs/OTC_WHITELABEL.md)**: Arquitetura e isolamento lógico.
- ⚙️ **[Engenharia do Microserviço](/docs/MICROSERVICE_OTC.md)**: Detalhes de Clean Architecture e SOLID.
- 🧪 **[Relatório de Testes](/docs/TESTS_OTC.md)**: Estratégia de testes e resiliência (Circuit Breaker).
- 🔑 **[Gestão de Chaves](/docs/chaves.md)**: Configurações de API e tokens.

---

## 🚀 Instalação e Setup

> [!WARNING]
> **Atenção ao Ambiente**: Atualmente o projeto recomenda o uso do Python 3.14 (localizado em `C:/Python314/python.exe` no ambiente de desenvolvimento).

### **Passos Rápidos**
1. **Clone o Repositório**:
   ```bash
   git clone https://github.com/seu-usuario/new-startse.git
   ```

2. **Configuração de Ambiente**:
   Recomendamos a criação de um ambiente virtual para rodar os novos microsserviços:
   ```bash
   /C/Python314/python.exe -m venv .venv
   source .venv/Scripts/activate
   ```

3. **Migrações de Banco de Dados**:
   ```bash
   python manage.py makemigrations otc
   python manage.py migrate
   ```

4. **Executando os Testes**:
   ```bash
   pytest otc-core-service/tests
   ```

---

## 🗺️ Roadmap de Evolução

- [x] Transição para Infraestrutura OTC
- [x] Implementação de Multi-tenancy Core
- [x] Design de Microsserviço OTC Core (SOLID)
- [x] Suíte de Testes e Circuit Breaker
- [ ] Interface UI para Negociação RFQ
- [ ] Dashboards Avançados por Tenant
- [ ] Liquidação em Blockchain (Smart Contracts)

---

## 🤝 Como Contribuir

Consulte o arquivo **[CONTRIBUTING.md](CONTRIBUTING.md)** (em breve) para diretrizes sobre como enviar Pull Requests seguindo nossos padrões de Clean Code.

---

## 📜 Licença

Este projeto é privado e de uso exclusivo para a infraestrutura **START-SE**. Todos os direitos reservados.
