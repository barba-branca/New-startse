# Guia de Alterações e Correções Recentes (Walkthrough)

Este documento descreve o passo a passo das correções e melhorias de layout, responsividade e integração realizadas recentemente no projeto **START-SE**.

---

## 1. Ajustes de Responsividade Mobile (Autenticação)

### Problema
Nas telas de Cadastro e Login, era exibido um bloco preto vazio de altura `100vh` no topo do celular, empurrando o formulário para baixo e simulando uma tela em branco.

### Causa Raiz
A coluna lateral da imagem (`col-md-2 bg-img`) continha a classe do Bootstrap `d-flex` que forçava um `display: flex !important;`, impedindo a ocultação pelo CSS em telas menores.

### Solução
Substituímos o controle por classes responsivas nativas do Bootstrap:
* **[cadastro.html](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/usuarios/templates/cadastro.html#L13):** Alterado para `col-md-2 d-none d-md-flex justify-content-center bg-img`
* **[logar.html](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/usuarios/templates/logar.html#L9):** Alterado para `col-md-2 d-none d-md-flex justify-content-center bg-img`

---

## 2. Redirecionamento para o Mercado Pago (Checkout Pro)

### Problema
Ao clicar em "Assinar Corporativo" ou outro plano pago, a aplicação redirecionava o usuário de volta para a página inicial em vez de encaminhá-lo para a tela de pagamentos do Mercado Pago.

### Causa Raiz
O Mercado Pago exige que a URL de sucesso (`back_urls.success`) utilize obrigatoriamente o protocolo **HTTPS** caso a opção `auto_return` esteja definida como `"approved"`. Como em ambiente local a URL iniciava com `http://127.0.0.1:8000`, a API retornava o erro:
`auto_return invalid. back_url.success must be defined`

### Solução
Atualizamos a lógica no utilitário [landingPage/utils.py](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/landingPage/utils.py#L80-L84) para converter a URL para HTTPS antes de enviá-la à API do Mercado Pago:
```python
    if base_url.startswith("http://"):
        base_url = base_url.replace("http://", "https://")
```

---

## 3. Melhorias de Responsividade na Landing Page Inicial

Corrigimos três principais problemas visuais identificados em visualizações mobile e tablet na página inicial:

### A. Correção da Sobreposição no Menu Mobile
* **Problema:** O menu lateral móvel exibia os botões de CTA ("Entrar" e "Começar Grátis") sobrepostos ao link "FAQ".
* **Solução:** No arquivo [landingPage/templates/index.html](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/landingPage/templates/index.html#L1759), substituímos o cálculo estático pelo cálculo de altura dinâmica em JavaScript:
  ```javascript
  top: ${70 + navLinks.getBoundingClientRect().height}px;
  ```

### B. Alinhamento dos Cards de Tecnologia (Tech Stack)
* **Problema:** A seção de tecnologias listava ícone, nome e descrição em uma única linha no celular, o que causava esmagamento do texto.
* **Solução:** No media query de `768px` de [index.html](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/landingPage/templates/index.html#L993-L1000), alteramos o layout para orientação em coluna:
  ```css
  .tech-item {
      flex-direction: column;
      align-items: center;
      text-align: center;
  }
  ```

### C. Alinhamento e Largura dos Planos (Pricing Cards)
* **Problema:** O card do plano **Corporativo** possuía largura de `255.9px` em resoluções tablet, divergindo do tamanho dos planos **Básico** e **Profissional** (`350px`).
* **Solução:**
  1. Definimos `width: 100%;` e `box-sizing: border-box;` na definição principal de `.pricing-card`.
  2. No media query de `992px` (tablet), mudamos a largura máxima do card para se ajustar ao grid de duas colunas subtraindo metade do gap de `20px`:
     ```css
     max-width: calc(50% - 10px);
     ```
  3. No media query de `768px` (mobile), resetamos para largura total:
     ```css
     max-width: 100%;
     margin: 0;
     ```

---

## 4. Implementação de Busca Avançada de Startups

Adicionamos a funcionalidade completa de **Busca Avançada** no módulo de investidores para permitir pesquisas e filtros minuciosos nas startups cadastradas.

### Solução
* **View (`investidores/views.py`):** Criada a view `busca_avancada(request)` que captura filtros via GET (nome, área, estágio, tempo de existência, valuation, equity e captação) e constrói a query dinamicamente utilizando a API de ORM do Django.
* **Valuation Dinâmico:** Como o valuation não é um campo físico do banco de dados, utilizamos `ExpressionWrapper` com `DecimalField` para realizar a filtragem numérica de valuation mínimo e máximo diretamente na query do banco de dados, evitando carregar objetos desnecessários em memória.
* **Layout (`busca_avancada.html`):** Desenvolvido um template responsivo completo utilizando checkboxes amigáveis para celular, cards estilizados com animações hover no grid, badges de status, e barras de progresso que mostram o percentual captado de cada startup.
* **Navegação:** Adicionado o link da busca ao menu global de navegação (`barra_navegacao.html`).
* **Testes unitários (`investidores/tests.py`):** Criamos 4 testes automatizados cobrindo a renderização do formulário, buscas textuais por nome e filtros específicos (área e valuation). Todos os testes foram executados e aprovados.

---

## 5. Implementação do Painel do Investidor (Dashboard)

Implementamos a funcionalidade completa de **Painel do Investidor** para suprir a necessidade de acompanhamento de portfólio, propostas de investimento e contratos digitais.

### Solução
* **View (`investidores/views.py`):** Criada a view `painel_investidor(request)` protegida pelo decorator `@login_required` para carregar as métricas agregadas (Total Alocado, Propostas Pendentes, Startups Apoiadas), o status de KYC do usuário e listar suas propostas e contratos associados.
* **Layout (`painel_investidor.html`):** Desenvolvido um dashboard com cards modernos de indicadores, tabela de propostas em tempo real com ações contextuais (como redirecionamento rápido para assinatura de contrato caso o status esteja pendente) e listagem de contratos digitais com suporte a downloads.
* **Navegação:** Adicionado o link "Painel do Investidor" ao menu global do header (`barra_navegacao.html`).
* **Testes unitários (`investidores/tests.py`):** Criados 2 novos testes automatizados para verificar o redirecionamento de usuários não autenticados e o cálculo correto das métricas no context para investidores logados. Todos os testes foram executados e aprovados.

---

## 6. Integração de IA para Sugestões de Investimento

Integramos inteligência artificial no módulo de **Sugestões de Investimento** (Marketplace) para dar justificativas de investimentos baseadas no perfil do investidor.

### Solução
* **Heurística Avançada com Fallback de IA (`sugestao` em `investidores/views.py`):** Integrada chamada ao Google Gemini (`gemini-1.5-flash`) ou Ollama local (`llama3`). A IA recebe os dados das startups pré-filtradas no orçamento do investidor, analisa a afinidade com o perfil (Conservador ou Despojado) e áreas de interesse, retornando as sugestões em JSON contendo justificativas personalizadas.
* **Fallback Seguro:** Caso as chaves de API estejam ausentes ou ocorra timeout das requisições, o sistema captura a exceção de forma transparente e aciona as regras heurísticas nativas do sistema.
* **Interface Visual Atualizada (`sugestao.html`):** Adicionado um switch switchable para ativar recomendações de IA, com a exibição de uma badge de autoria ("Fonte das Sugestões: Inteligência Artificial") e contêineres de justificativas estilizados em roxo-glowing nos cards de startups.
* **Testes unitários (`investidores/tests.py`):** Adicionados 3 novos testes cobrindo a filtragem tradicional (conservadora/despojada) e garantindo que o fallback ocorra sem erros no caso de falta de chaves ou indisponibilidade de IA.



