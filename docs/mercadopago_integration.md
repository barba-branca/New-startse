# Integração Mercado Pago - Documentação

Este documento detalha a integração com a API do Mercado Pago para assinaturas e pagamentos na plataforma New StartSE.

## Visão Geral

A integração permite que usuários assinem planos (Profissional, Corporativo) diretamente pela landing page. Utilizamos o SDK oficial do Mercado Pago para Python (`mercadopago`) para criar preferências de pagamento.

## Configuração

### Variáveis de Ambiente (.env)

As seguintes variáveis devem estar configuradas no arquivo `.env`:

```bash
MERCADO_PAGO_ACCESS_TOKEN=seu_access_token_aqui
MERCADO_PAGO_PUBLIC_KEY=sua_public_key_aqui
```

> **Nota**: Tokens de teste e produção são diferentes. Certifique-se de usar o token correto para o ambiente desejado.

### Dependências

A biblioteca `mercadopago` deve estar instalada:

```bash
pip install mercadopago
```

## Estrutura do Código

### 1. Utilitários (`landingPage/utils.py`)

A função `create_checkout_preference` é responsável por comunicar com a API do Mercado Pago.

**Assinatura:**
```python
def create_checkout_preference(user, plan_name, price):
    # ...
```

- **user**: Objeto usuário do Django (usa `first_name`, `last_name`, `email`).
- **plan_name**: Nome do plano (ex: "Profissional").
- **price**: Preço do plano (float).

**Retorno**: URL de checkout (`init_point`) ou `None` em caso de erro.

### 2. Views (`landingPage/views.py`)

A view `checkout` gerencia o fluxo:
1. Verifica se o usuário está logado (`@login_required`).
2. Identifica o plano selecionado (via URL parameter).
3. Chama `create_checkout_preference`.
4. Redireciona para o Mercado Pago.

### 3. URLs (`landingPage/urls.py`)

A rota `/checkout/<plan_id>/` mapeia para a view de checkout.

## Testando a Integração

Para verificar se a integração está funcionando corretamente:

1. **Configuração**: Verifique se as credenciais no `.env` estão corretas.
2. **Fluxo de Usuário**:
    - Logue na plataforma.
    - Na landing page, clique em "Assinar Agora" no plano desejado.
    - Se for redirecionado para o Mercado Pago com o valor correto, a integração está funcionando.
3. **Script de Teste (Opcional)**:
    Você pode criar um script temporário para testar a função `create_checkout_preference` isoladamente:

    ```python
    import os
    import django
    from django.conf import settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()

    from landingPage.utils import create_checkout_preference
    
    # Simular usuário
    class User:
        first_name = "Teste"
        last_name = "User"
        email = "teste@exemplo.com"
    
    url = create_checkout_preference(User(), "Teste", 10.00)
    print(url)
    ```

## Próximos Passos (Melhorias)

- **Webhooks**: Implementar endpoint para receber notificações de pagamento (IPN) e ativar a assinatura automaticamente.
- **Cancelamento**: Adicionar fluxo para cancelamento de assinatura.
- **Histórico**: Salvar histórico de pagamentos no banco de dados local.
