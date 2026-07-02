# 🗑️ Documentação: Remoção do Mercado Pago

**Autor:** Barba-Branca  
**Data:** 02/07/2026  
**Status:** Concluído  

---

## 📌 Visão Geral

Esta documentação descreve o processo de descontinuação e remoção completa da integração do gateway de pagamento **Mercado Pago** no projeto **New Start-se**. O processamento de pagamentos foi centralizado e unificado através do **Stripe**, simplificando a arquitetura do sistema e eliminando redundâncias.

---

## 🛠️ Alterações e Limpeza de Código

A remoção do Mercado Pago impactou diversos módulos do monólito Django, exigindo a limpeza de rotas, views, utilitários, configurações e dependências do projeto.

### 1. Limpeza de Configurações (`core/settings.py`)
Removidas as variáveis de ambiente que armazenavam as credenciais da API do Mercado Pago:
- `MERCADO_PAGO_ACCESS_TOKEN`
- `MERCADO_PAGO_PUBLIC_KEY`

### 2. Remoção de Dependências (`requirements.txt`)
- Removida a linha contendo o pacote SDK oficial `mercadopago`, reduzindo o número de dependências externas instaladas no ambiente da aplicação.

### 3. Remoção de Utilitários de Checkout (`landingPage/utils.py`)
- **Deletada a função `create_checkout_preference`**: Essa função montava o dicionário contendo itens, dados do pagador e as URLs de retorno (`back_urls`), enviando-os para a API do Mercado Pago a fim de gerar o link do checkout (Checkout Pro).
- Removido o import `import mercadopago`.

### 4. Remoção de Webhooks e Views (`landingPage/views.py`)
- **Deletada a view `webhook_mercadopago`**: Responsável por receber notificações IPN pós-pagamento.
- **Simplificação da view `checkout`**: Anteriormente, essa view chamava a API do Mercado Pago para gerar a preferência de pagamento. Agora, ela ativa o plano trial gratuito diretamente no sistema.

### 5. Exclusão de Rotas (`landingPage/urls.py`)
- Removida a rota `/webhooks/mercadopago/` de recepção de eventos do Mercado Pago.

---

## 📊 Motivos da Mudança
- **Unificação Tecnológica:** Evita a manutenção de dois SDKs de pagamentos diferentes (Stripe e Mercado Pago).
- **Segurança:** O Stripe Connect foi adotado para o split de pagamentos das mesas OTC, tornando-o o gateway padrão de toda a plataforma.
- **Simplificação do Fluxo:** Remoção de redirecionamentos complexos externos para o checkout de planos na landing page durante a fase promocional e beta.
