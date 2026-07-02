# Registro de Alterações (Changelog)

Todas as alterações notáveis a este projeto serão registradas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
e este projeto segue o [Versionamento Semântico](https://semver.org/spec/v2.0.0.html).

## [Não lançado]

### Adicionado
- Implementação do **Painel do Investidor (Dashboard)** (`/investidores/painel/`), com métricas de portfólio, verificação cadastral (KYC), tabela de propostas e controle de contratos digitais.
- Novo template responsivo (`painel_investidor.html`) com cards de métricas e tabelas dinâmicas.
- Adicionados testes automatizados de controle de acesso e cálculo de métricas para o painel em `investidores/tests.py`.
- Documentação técnica detalhada do painel criada em `docs/painel_investidor.md`.
- Implementação da **Busca Avançada de Startups** (`/investidores/busca_avancada/`), com filtros por nome, áreas de atuação, estágio, tempo de existência, valuation, equity e meta de captação.
- Novo template moderno e responsivo (`busca_avancada.html`) com barras de progresso dinâmicas nos resultados.
- Adicionados testes de integração e validação de filtros em `investidores/tests.py`.
- Documentação técnica detalhada criada em `docs/busca_avancada_startups.md`.
- Integração de **IA para Sugestões de Investimento** com justificativas inteligentes personalizadas e fallback seguro de regras de negócio.
- Documentação técnica detalhada das sugestões de IA criada em `docs/sugestoes_ia.md`.
- Criado `docs/saka_system.md` documentando o funcionamento do **Sistema S.A.K.A. (CrewAI)**.
- Criado `docs/AGENT_ROLES.md` para definir os papéis dos agentes.
- Estabelecido o papel de "Bibliotecário" (Agente de Documentação).
- Organizada a estrutura de documentação na pasta `docs/`.

### Alterado
- Movido o `README.md` de `docs/` para a raiz do projeto para melhor visibilidade.

### Corrigido
- **Login do Google**: Implementado um fallback no código para o `GOOGLE_CLIENT_ID` em `core/settings.py` para resolver o erro `invalid_client` (401) nas implantações do Azure onde as variáveis de ambiente estavam falhando.
- **Listagem de Empresas**: Corrigido um erro `TemplateSyntaxError` (500) em `empresarios/templates/listar_empresas.html` provocado por uma tag `{% endif %}` malformada/dividida.

## [1.1.0] - 2026-04-16

### Adicionado
- **Real-time Ticker**: Implementação de ticker financeiro em tempo real usando JavaScript puro (sem dependências de backend).
- **Multi-API Integration**: Integração com Binance API (Cripto) e AwesomeAPI (Câmbio) para dados atualizados.
- **Developer Branding**: Adicionada a assinatura "Produzido por Develops Code" em todas as páginas e no README.

### Alterado
- **Global Rebranding**: O projeto foi oficialmente renomeado de "STARTSE" para **New Start-se** em todo o frontend, títulos e documentação.
- **Frontend Decoupling**: Removida a dependência do `yfinance` no backend para evitar erros de DLL no Windows, movendo a lógica para o lado do cliente.

### Corrigido
- **Estabilização do Servidor**: Implementados stubs e mocks para bibliotecas bloqueadas pelo Windows App Control, garantindo que o `runserver` opere sem travamentos.

---
**Documentação feita por Barba-Branca.**

