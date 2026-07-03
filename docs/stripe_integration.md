# Documentação: Integração com Stripe (Crowdfunding & Split de Pagamento)

**Autor:** Barba-Branca

Este documento detalha as configurações e o funcionamento da integração do **Stripe** no ecossistema da **New Start-se**, cobrindo a assinatura de planos pela Landing Page e o Split de Pagamento automático de propostas com 2% de taxa.

---

## ⚙️ Variáveis de Ambiente (.env / Vercel)

Para configurar a comunicação com o gateway do Stripe, adicione as seguintes credenciais ao seu arquivo `.env` de desenvolvimento e configure as variáveis no painel da Vercel para produção:

```env
# Stripe Keys (Sandbox / Produção)
STRIPE_PUBLIC_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 💳 1. Planos e Checkout na Landing Page

A Landing Page exibe três opções de planos para investidores:
1. **Plano Pro Trial**: Gratuito por 7 dias (ativado imediatamente).
2. **Plano Profissional**: R$ 99,00 / mês (redireciona para Stripe Checkout).
3. **Plano Corporativo**: R$ 299,00 / mês (redireciona para Stripe Checkout).

### Fluxo Técnico:
- Quando o usuário clica para assinar um plano pago, a view `checkout` em [landingPage/views.py](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/landingPage/views.py) cria uma sessão de checkout do Stripe via `stripe.checkout.Session.create`.
- O usuário é redirecionado ao formulário de pagamento seguro hospedado pelo Stripe.
- Ao concluir ou cancelar, o usuário retorna à Landing Page com parâmetros de status (`?payment=success` ou `?payment=cancel`), exibindo notificações amigáveis via mensagens do Django.

---

## 💸 2. Débito Automático e Split de Investimento (2% de Taxa)

Quando uma proposta de investimento é aceita pelo empresário fundador da startup na view `gerenciar_proposta` em [empresarios/views.py](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/empresarios/views.py), o sistema realiza automaticamente o débito e a divisão (split):

### Regras de Negócio e Percentual:
- **Taxa de Intermediação (Plataforma)**: **2%** do valor total aportado.
- **Valor Líquido (Startup)**: **98%** do valor total aportado.

### Fluxo Técnico do Split (Stripe Connect):
1. **Stripe Customer**: Um cliente Stripe é recuperado ou criado dinamicamente para o investidor usando seu e-mail.
2. **Stripe Connected Account**: Uma conta conectada customizada (`stripe.Account.create`) é criada em tempo real para a startup/empresário.
3. **PaymentIntent com Split**: É emitido um `stripe.PaymentIntent` do valor total contendo:
   - `application_fee_amount`: O valor correspondente aos 2% da plataforma.
   - `transfer_data`: Configurado com o destino (`destination`) apontando para a conta conectada do empresário.
   - `confirm=True` e `payment_method="pm_card_visa"`: Força a cobrança automática imediata em modo sandbox/testes.
4. **Resiliência (Fallback)**: Caso o Stripe não esteja configurado localmente ou suas credenciais estejam ausentes, o sistema realiza o processamento local, atualizando a proposta e as taxas da startup no banco de dados local para garantir que a plataforma continue plenamente funcional.

---
*Documentação de integração elaborada sob a coordenação de Barba-Branca.*
