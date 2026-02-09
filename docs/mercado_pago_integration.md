# Integração Mercado Pago - New StartSE

Este documento detalha a implementação da integração com o Mercado Pago para processamento de pagamentos (Checkout Pro) e recebimento de notificações (Webhooks/IPN).

## 1. Configuração

Para que a integração funcione, as seguintes variáveis de ambiente devem estar configuradas (tanto localmente no `.env` quanto no Azure App Service):

```bash
MERCADO_PAGO_ACCESS_TOKEN=APP_USR-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MERCADO_PAGO_PUBLIC_KEY=APP_USR-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

## 2. Fluxo de Checkout

O checkout é realizado através do **Checkout Pro** do Mercado Pago.
- **Arquivo**: `landingPage/utils.py` -> `create_checkout_preference`
- **Funcionamento**: Cria uma preferência de pagamento com os itens do plano selecionado.
- **Retorno**: Redireciona o usuário para o `init_point` (URL de pagamento do Mercado Pago).
- **Auto Return**: Configurado como `approved`, ou seja, se o pagamento for aprovado, o usuário é redirecionado automaticamente de volta para o site.

### URLs de Retorno
- **Sucesso**: `/empresa/cadastrar_empresa/` (Redireciona para o cadastro após pagamento)
- **Falha**: `/?status=failure`
- **Pendente**: `/?status=pending`

## 3. Webhook (Notificações IPN)

O sistema escuta notificações de atualizações de pagamento enviadas pelo Mercado Pago.

- **Endpoint**: `/landingPage/webhooks/mercadopago/`
- **View**: `landingPage/views.py` -> `webhook_mercadopago`
- **Configuração no Mercado Pago**:
    1. Acesse [Seu Dashboard de Aplicações](https://www.mercadopago.com.br/developers/panel/app).
    2. Selecione a aplicação.
    3. Em **Webhooks**, configure a URL de produção: `https://<SEU-DOMINIO-AZURE>/landingPage/webhooks/mercadopago/`
    4. Selecione o evento: **Pagamentos** (Payments).

## 4. Scripts de Teste

Foram criados scripts para validar a integração e as credenciais:

### Testar Credenciais (`scripts/test_mercadopago.py`)
Tenta criar uma preferência de teste para verificar se o `ACCESS_TOKEN` é válido.
```bash
python scripts/test_mercadopago.py
```

### Simular Webhook (`scripts/test_webhook_simulation.py`)
Simula uma requisição POST de webhook (como se fosse o Mercado Pago) para testar se a view está processando corretamente.
```bash
python scripts/test_webhook_simulation.py
```
