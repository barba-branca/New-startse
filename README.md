# 🚀 New Start-se: Plataforma de Equity Crowdfunding & Matching

A **New Start-se** é uma **plataforma de ponta para Equity Crowdfunding e Matching de Startups**. Projetada para conectar investidores anjo a startups promissoras em busca de captação de recursos, ela combina o poder do Django com uma arquitetura de microsserviços limpa, garantindo alta performance, segurança e escalabilidade.

---

## 🌟 Visão Geral

A plataforma permite:
- **Cadastro e Listagem de Startups**: Fluxo robusto de cadastro de empresas e captação de recursos.
- **Painel do Investidor**: Portfólio, propostas pendentes, contratos e status de KYC.
- **Sugestões por IA (Kamila)**: Recomendações e análise de viabilidade personalizadas com inteligência artificial para auxiliar investidores.
- **Integração de Pagamentos**: Assinaturas de planos e checkout via Stripe.
- **Segregação de Perfis & Segurança**: Cadastro segregado com validação de CNPJ automatizada (Receita Federal) para Investidores PJ e Empresários/Startups, restringindo acessos a painéis inadequados através de controle de rotas.

---

## 🏗️ Arquitetura do Sistema

O projeto utiliza o **Monólito Central (Django)** de forma modular, com as responsabilidades e regras de negócios divididas entre apps específicos:
- **usuarios**: Cadastro, login, perfis e controle de acessos.
- **empresarios**: Cadastro de empresas, publicação de rodadas de captação de recursos e acompanhamento de propostas de investimento.
- **investidores**: Busca avançada de startups, marketplace de investimentos, assinatura de contratos e sugestões assistidas por IA.
- **landingPage**: Páginas promocionais, FAQ, e controle de planos/checkout do site.

---

## 🛠️ Tecnologias Principais

- **Backend**: Django 5.1 & Python 3.12+
- **Banco de Dados**: SQLite em desenvolvimento / PostgreSQL em produção
- **IA/Agentes**: Integração com Google Gemini para justificativas de investimentos
- **Gateways**: Integração de Pagamento Stripe e Assinatura Digital via ZapSign

---

## 📚 Documentação Técnica

Para detalhes aprofundados, consulte nossa pasta **[`docs/`](/docs)**:

- 🔑 **[Gestão de Chaves](/docs/chaves.md)**: Configurações de API e tokens.

---

## 🚀 Instalação e Setup

### **Passos Rápidos**
1. **Clone o Repositório**:
   ```bash
   git clone https://github.com/seu-usuario/new-startse.git
   ```

2. **Configuração de Ambiente**:
   Recomendamos a criação de um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows (PowerShell: .\venv\Scripts\Activate.ps1)
   ```

3. **Instalação das Dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Migrações de Banco de Dados**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Executando o Servidor**:
   ```bash
   python manage.py runserver
   ```

---

## 🗺️ Roadmap de Evolução

### Módulo Crowdfunding & Matching:
- [x] Cadastro de empresas
- [x] Listagem de startups
- [x] Implementação do módulo de investidores
- [x] Funcionalidade de busca avançada
- [x] Integração com meios de pagamento (Stripe)
- [x] Integração de IA para análises e sugestões
- [x] Separação de Perfis (Investidor vs. Empresário)
- [x] Validação de CNPJ automatizada (Brasil API/Receita Federal) no cadastro
- [ ] Melhorias no painel administrativo de campanhas

---

## 9. Documentação Adicional

Para guias de instalação detalhados, alterações recentes e notas técnicas, consulte os documentos na pasta `docs/`:
- [Guia de Alterações Recentes (Walkthrough)](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/docs/walkthrough.md): Passo a passo das correções de layout e responsividade, busca avançada, painel do investidor, sugestões por IA e o processo de **remoção completa do módulo OTC**.
- [Configuração e Integração com Stripe](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/docs/stripe_integration.md): Detalhes sobre a configuração das chaves e webhooks do Stripe.
- [Separação de Perfis & Validação CNPJ](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/docs/user_profile_separation.md): Estrutura do PerfilUsuario, cadastro segregado e decorators de acesso.
- [KYC Inteligente & Contratos por IA](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/docs/kyc_and_contract_ai.md): Processamento multimodal anti-fraude de selfies/RG e redação de contratos por IA com timestamps.
- [Ajustes de Responsividade Mobile](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/docs/fix_mobile_responsiveness.md): Detalhes técnicos sobre a responsividade das páginas de autenticação e da landing page.
- [Migração para PostgreSQL e Azure](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/docs/postgresql_migration.md): Passos para configuração do banco de dados em produção.

---

## 🔄 Refatoração Recente: Remoção do Módulo OTC

Para manter a plataforma focada em sua proposta de valor original e evitar complexidade desnecessária no monólito, foi realizada uma refatoração estrutural completa para remover o módulo **OTC White Label**:
* **Middleware e Roteamento**: Exclusão do controle de multi-tenancy (`core/multitenancy.py`) e remoção das rotas `/otc/` em `urls.py`.
* **Remoção de Código e Serviços**: Eliminação dos diretórios do app Django `otc/` e do microsserviço `otc-core-service/`.
* **Simplificação do Ambiente**: Limpeza das dependências de terceiros (`stripe` e `yfinance`) no arquivo `requirements.txt`.
* **Consolidação**: A suíte de testes do monólito (`usuarios`, `empresarios` e `investidores`) foi executada com sucesso garantindo estabilidade pós-remoção.

---

## ☁️ Deploy na Vercel

A **New Start-se** está pronta para ser implantada na Vercel.

### **Pré-requisitos**
1. **Banco de Dados**: Como a Vercel é stateless, o SQLite não funcionará para persistência. Utilize um banco **PostgreSQL** (Ex: Neon.tech).
2. **Variáveis de Ambiente**: Configure as seguintes variáveis no painel da Vercel:
   - `DJANGO_SECRET_KEY`: Uma chave aleatória segura.
   - `DATABASE_URL`: URL de conexão do seu PostgreSQL.
   - `DEBUG`: `False` (em produção).
   - `ZAPSIGN_API_TOKEN`, `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, etc.

### **Como subir**
1. Conecte seu repositório GitHub à Vercel.
2. A Vercel detectará o `vercel.json` e o `requirements.txt` automaticamente.
3. O comando de build executará `python manage.py collectstatic` ou utilizará o **WhiteNoise** já presente no projeto.

---

## 🤝 Como Contribuir

Consulte o arquivo **[CONTRIBUTING.md](CONTRIBUTING.md)** (em breve) para diretrizes sobre como enviar Pull Requests seguindo nossos padrões de Clean Code.

---

## 📜 Licença

Este projeto é privado e de uso exclusivo para a infraestrutura **New Start-se**. Todos os direitos reservados.

---
🚀 **Produzido por [Develops Code](https://developscode.com.br)**  
✍️ **Documentação por: Barba-Branca**
