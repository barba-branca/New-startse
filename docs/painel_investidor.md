# Documentação: Painel do Investidor (Dashboard)

Esta documentação descreve a arquitetura, o design e as métricas do **Painel do Investidor** implementado na plataforma **START-SE**.

---

## 1. Visão Geral

O Painel do Investidor é a central de controle para investidores cadastrados acompanharem suas atividades financeiras e contratuais na plataforma. Ele atua como o ecossistema complementar à visão do empresário, permitindo que os investidores tenham visibilidade total dos seus aportes ativos, propostas sob análise e contratos assinados de forma eletrônica.

---

## 2. Estrutura de Métricas do Portfólio

O painel agrega e exibe em tempo real quatro indicadores essenciais na parte superior da interface:

1. **Total Alocado (R$)**:
   - Representa a soma financeira de todas as propostas com status `PA` (Proposta Aceita).
   - Mostra o capital real já investido pelo usuário.
2. **Propostas Pendentes**:
   - Contagem de propostas ativas nos estados `AS` (Aguardando Assinatura) e `PE` (Proposta Enviada para análise do empresário).
3. **Startups Apoiadas**:
   - Número de empresas distintas que aceitaram pelo menos uma proposta do investidor.
4. **Status do KYC (Know Your Customer)**:
   - Exibe o status da validação cadastral obrigatória do investidor e o percentual de score de fraude calculado pela plataforma.

---

## 3. Gestão de Propostas e Contratos

A interface é dividida em duas tabelas interativas:

### A. Minhas Propostas de Investimento
Lista todas as propostas efetuadas pelo investidor (`PropostaInvestimento`), contendo:
- Nome da startup (com logotipo e área de atuação).
- Valor total ofertado.
- Equity (%) solicitado.
- Valuation implícito calculado a partir da oferta.
- Badge colorido indicando o status atual (`Aguardando Assinatura`, `Enviada para Análise`, `Aprovada` ou `Recusada`).
- **Ação Contextual**: Se a proposta estiver em `AS` (Aguardando Assinatura), exibe o botão destacado **Assinar Contrato** para redirecionar o investidor à etapa de assinatura. Caso contrário, exibe o botão **Ver Detalhes** para visualizar a startup.

### B. Meus Contratos Digitais
Acompanha todos os contratos gerados (`ContratoDigital`), exibindo:
- Nome da startup associada.
- Tipo do Contrato (ex: Mútuo Conversível, SAFE, NDA).
- Data e hora da emissão.
- Status do Contrato (Rascunho, Pendente, Enviado, Parcialmente Assinado, Totalmente Assinado).
- **Download**: Botão ativo para baixar o documento final assinado em formato PDF quando finalizado pela plataforma de assinatura digital.

---

## 4. Implementação Técnica

### A. Segurança e Controle de Acesso (`investidores/views.py`)
A view `painel_investidor` exige autenticação obrigatória via `@login_required`:
```python
@login_required(login_url='/usuarios/logar/')
def painel_investidor(request):
    ...
```

### B. Rotas e URL (`investidores/urls.py`)
A rota é acessada em `/investidores/painel/`:
```python
path('painel/', views.painel_investidor, name="painel_investidor"),
```

### C. Menu Principal (`templates/partials/barra_navegacao.html`)
Adicionado o link **Painel do Investidor** para fácil acesso.

---

## 5. Testes Unitários (`investidores/tests.py`)

A classe `PainelInvestidorTestCase` foi adicionada para garantir o funcionamento correto:
- **`test_painel_investidor_anonymous_redirect`**: Garante o redirecionamento correto (HTTP 302) para a tela de login se um usuário anônimo tentar acessar o painel.
- **`test_painel_investidor_authenticated`**: Simula login de investidor, realiza duas propostas com status diferentes e verifica se as variáveis do context (`total_investido`, `propostas_pendentes` e `startups_apoiadas`) retornam com os valores corretos.
