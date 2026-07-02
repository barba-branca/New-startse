# 🚀 New Start-se: Infraestrutura White Label OTC

A **New Start-se** evoluiu de uma plataforma de crowdfunding para uma **infraestrutura White Label de ponta para mesas de negociação OTC (Over-The-Counter)**. Projetada para alta performance, ela combina o poder do Django com uma arquitetura de microsserviços limpa (Clean Architecture), garantindo escalabilidade e isolamento total entre diferentes operadoras (Desks).

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
- **Frontend Real-time**: Ticker financeiro dinâmico (Binance & AwesomeAPI)
- **Arquitetura**: Clean Architecture / Microsserviços
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

<<<<<<< HEAD
- [x] Transição para Infraestrutura OTC
- [x] Implementação de Multi-tenancy Core
- [x] Design de Microsserviço OTC Core (SOLID)
- [x] Suíte de Testes e Circuit Breaker
- [ ] Interface UI para Negociação RFQ
- [ ] Dashboards Avançados por Tenant
- [ ] Liquidação em Blockchain (Smart Contracts)

---

## ☁️ Deploy na Vercel
=======
- [x] Cadastro de empresas
- [x] Listagem de startups
- [x] Implementação do módulo de investidores
- [x] Funcionalidade de busca avançada
- [x] Integração com meios de pagamento (Mercado Pago)
- [x] Integração de IA para análises e sugestões

---

## **9. Documentação Adicional**

Para guias de instalação detalhados, alterações recentes e notas técnicas, consulte os documentos na pasta `docs/`:
- [Guia de Alterações Recentes (Walkthrough)](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/docs/walkthrough.md): Passo a passo das correções de layout e responsividade do menu mobile, cards de tecnologia, alinhamento dos planos e integração com o Mercado Pago.
- [Ajustes de Responsividade Mobile](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/docs/fix_mobile_responsiveness.md): Detalhes técnicos sobre a responsividade das páginas de autenticação e da landing page.
- [Correção do Redirecionamento do Mercado Pago](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/docs/fix_mercadopago_redirect.md): Informações sobre a correção de URLs HTTPS necessárias para o checkout e instruções de teste mobile.
- [Migração para PostgreSQL e Azure](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/docs/postgresql_migration.md): Passos para configuração do banco de dados em produção.

---

## **10. Como Contribuir**
>>>>>>> 775917e (feat(investidores): add advanced search, investor dashboard, and AI-powered suggestions)

A **New Start-se** está pronta para ser implantada na Vercel.

### **Pré-requisitos**
1. **Banco de Dados**: Como a Vercel é stateless, o SQLite não funcionará para persistência. Utilize um banco **PostgreSQL** (Ex: Neon.tech).
2. **Variáveis de Ambiente**: Configure as seguintes variáveis no painel da Vercel:
   - `DJANGO_SECRET_KEY`: Uma chave aleatória segura.
   - `DATABASE_URL`: URL de conexão do seu PostgreSQL.
   - `DEBUG`: `False` (em produção).
   - `ZAPSIGN_API_TOKEN`, `MERCADO_PAGO_ACCESS_TOKEN`, etc.
   - `STRIPE_PUBLIC_KEY`: Chave pública do Stripe (Sandbox/Produção).
   - `STRIPE_SECRET_KEY`: Chave secreta do Stripe (Sandbox/Produção).
   - `STRIPE_WEBHOOK_SECRET`: Segredo de validação de assinatura do webhook do Stripe.


### **Como subir**
1. Conecte seu repositório GitHub à Vercel.
2. A Vercel detectará o `vercel.json` e o `requirements.txt` automaticamente.
3. O comando de build executará `python manage.py collectstatic` (se configurado) ou utilizará o **WhiteNoise** já presente no projeto.

---

## 🤝 Como Contribuir

Consulte o arquivo **[CONTRIBUTING.md](CONTRIBUTING.md)** (em breve) para diretrizes sobre como enviar Pull Requests seguindo nossos padrões de Clean Code.

---

## 📜 Licença

Este projeto é privado e de uso exclusivo para a infraestrutura **New Start-se**. Todos os direitos reservados.

---
🚀 **Produzido por [Develops Code](https://developscode.com.br)**  
✍️ **Documentação por: Barba-Branca**
