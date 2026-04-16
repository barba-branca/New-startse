# DOCUMENTAÇÃO TÉCNICA: New Start-se

## 1. Visão Geral
A **New Start-se** é uma plataforma de crowdfunding e investment-matching projetada para o ecossistema de startups brasileiro. Ela atua como uma ponte digital entre empreendedores em busca de capital e investidores procurando oportunidades de alto crescimento. O diferencial da plataforma reside na integração de Inteligência Artificial para análise de risco, due diligence e auxílio na tomada de decisão.

---

## 2. Arquitetura do Sistema

O projeto é construído sobre o framework **Django (Python)**, seguindo o padrão MVT (Model-View-Template).

### Estrutura de Pastas e Apps:
- `core/`: Configurações centrais do Django, URLs principais e definições de ambiente.
- `usuarios/`: Gerenciamento de autenticação, perfis e controle de acesso.
- `landingPage/`: Interface pública, marketing, integração com dados da B3 e pagamentos via Mercado Pago.
- `empresarios/`: Core business para empreendedores (cadastro de startups, métricas, documentos e IA de pitch).
- `investidores/`: Core business para investidores (propostas, Data Room, KYC e Assinatura Digital).
- `saka_system/`: Sistema autônomo de agentes (CrewAI) para análises complexas.
- `media/`: Armazenamento de arquivos enviados (Pitches, Logos, Documentos).
- `templates/`: Arquivos HTML globais e componentes de interface.

---

## 3. Módulos Detalhados

### 3.1. Empresários (Startups)
O módulo de empresários permite a gestão completa do ciclo de captação:
- **Modelo `Empresas`**: Armazena CNPJ, estágio (Idea, MVP, Scalable), área (Edtech, Fintech, etc), valuation e equity oferecido.
- **Métricas e Documentos**: Sistema dinâmico para acompanhamento de KPIs e armazenamento de PDFs.
- **Valuation Projeção**: Lógica embutida para projetar o crescimento do valor da empresa em 5 anos.
- **Análise de Pitches com IA**: Integração com **Ollama (Local)** ou **Google Gemini** para fornecer feedbacks automáticos sobre a descrição do negócio.

### 3.2. Investidores
Focado em segurança e transparência:
- **Propostas de Investimento**: Fluxo de negociação com status (Aguardando Assinatura, Enviada, Aceita, Recusada).
- **KYC (Know Your Customer)**: Verificação de identidade com envio de selfie e RG.
- **Data Room**: Área segura onde documentos confidenciais são liberados apenas para investidores com "Match" ou propostas em andamento.
- **Assinatura Digital**: Integração via API com **ZapSign/Clicksign** para formalização jurídica de contratos de Mútuo Conversível e SAFE.

### 3.3. Landing Page & Monetização
- **Real-time Ticker**: Implementação em JavaScript que consome APIs da Binance (Cripto) e AwesomeAPI (Câmbio) para exibir cotações em tempo real sem dependências de backend.
- **Checkout Mercado Pago**: Integração para planos de assinatura (Profissional/Corporativo), com sistema de Webhook para liberação automática de recursos.

---

## 4. O Sistema S.A.K.A. (AI Agents)

A plataforma conta com um sistema de agentes baseado em **CrewAI** para orquestração de tarefas:
- **Kamila (CEO)**: Orquestradora estratégica que delega tarefas.
- **Thoth (NLP)**: Especialista em processamento de linguagem natural e extração de insights.
- **Hera (Visão)**: Analista multimodal para OCR de notas fiscais e documentos visuais.
- **Hermes (Dados)**: Engenheiro de dados e APIs para cálculos financeiros complexos.

O sistema utiliza **Ollama (Llama3 e Llava)** como backend de processamento local na VPS.

---

## 5. Integrações Externas

| Serviço | Utilidade | Status |
| :--- | :--- | :--- |
| **ZapSign** | Assinatura digital de contratos de investimento. | Implementado |
| **Mercado Pago** | Processamento de pagamentos para planos de uso. | Implementado |
| **Ollama** | Execução local de LLMs para análise e OCR. | Implementado |
| **Google Gemini** | Alternativa em nuvem para análises de IA. | Opcional |
| **Azure Storage** | Armazenamento de arquivos em ambiente de produção. | Opcional |

---

## 6. Guia de Instalação e Execução

### Requisitos Técnicos:
- **Python 3.10+**
- **Ollama** (para funcionalidades de IA locais)
- **Pipenv** ou **Requirements.txt**

### Comandos de Inicialização:
1. Instalar dependências: `pip install -r requirements.txt`
2. Aplicar migrações: `python manage.py migrate`
3. Criar Superusuário: `python manage.py createsuperuser`
4. Iniciar Servidor: `python manage.py runserver`

### Configuração de IA (Ollama):
Para o pleno funcionamento das análises, execute:
```bash
ollama pull llama3.2
ollama pull llava
```

---

## 7. Próximos Passos (Roadmap)
- [ ] Implementação total do módulo de leilão competitivo.
- [ ] Busca avançada com filtros de inteligência geográfica.
- [ ] Dashboard de performance consolidada para investidores.
- [ ] Multi-tenancy para aceleradoras de startups.

---
**Documentação gerada automaticamente pela Antigravity AI.**
