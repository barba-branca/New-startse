import os
import mercadopago
from django.conf import settings

def get_b3_data():
    """
    Desativado: Agora o ticker é controlado via Frontend (JavaScript) 
    para maior estabilidade e performance em tempo real.
    """
    return []

def create_checkout_preference(request, user, plan_name, price):
    """
    Cria uma preferência de pagamento no Mercado Pago.
    Retorna (url_checkout, erro) - onde erro é None se sucesso.
    """
    if not settings.MERCADO_PAGO_ACCESS_TOKEN:
        return None, "Integração com Mercado Pago não configurada. Entre em contato com o suporte."

    # Nome do pagador - Mercado Pago exige nome não vazio
    first_name = (user.first_name or user.username or "Cliente").strip()
    last_name = (user.last_name or "").strip()
    email = (user.email or "").strip()
    if not email:
        email = f"{user.username}@newstartse.placeholder"  # fallback para usuários sem email

    # Determinar URL base de forma robusta (Azure / Local)
    base_url = os.environ.get('BASE_URL')
    if not base_url:
        website_hostname = os.environ.get('WEBSITE_HOSTNAME')
        if website_hostname:
            base_url = f"https://{website_hostname}"
        else:
            base_url = request.build_absolute_uri("/").rstrip("/")

    success_url = f"{base_url}/empresarios/cadastrar_empresa/"
    failure_url = f"{base_url}/?status=failure"
    pending_url = f"{base_url}/?status=pending"

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    preference_data = {
        "items": [
            {
                "title": f"Plano {plan_name} - New StartSE",
                "quantity": 1,
                "unit_price": float(price),
                "currency_id": "BRL"
            }
        ],
        "payer": {
            "name": first_name,
            "surname": last_name or ".",
            "email": email,
        },
        "back_urls": {
            "success": success_url,
            "failure": failure_url,
            "pending": pending_url
        },
        "auto_return": "approved",
    }

    try:
        preference_response = sdk.preference().create(preference_data)
    except Exception as e:
        return None, f"Erro ao conectar com Mercado Pago: {str(e)}"

    if "response" in preference_response:
        response = preference_response["response"]
        if "init_point" in response:
            return response["init_point"], None
        # API pode retornar erro dentro do response
        if "status" in response and response.get("status") >= 400:
            msg = response.get("message", "Erro desconhecido do Mercado Pago")
            return None, f"Mercado Pago: {msg}"

    # Resposta com erro explícito
    if "error" in preference_response:
        err = preference_response["error"]
        msg = err.get("message", str(err))
        return None, f"Mercado Pago: {msg}"

    return None, "Não foi possível gerar o link de pagamento. Tente novamente."
