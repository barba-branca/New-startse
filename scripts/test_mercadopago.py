import os
import sys
import mercadopago
from dotenv import load_dotenv
from pathlib import Path

# Adiciona o diretório raiz ao path para importar settings se necessário, 
# mas aqui vamos usar apenas as env vars diretamente para isolar o teste
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

def test_mercadopago_connection():
    access_token = os.getenv('MERCADO_PAGO_ACCESS_TOKEN')
    public_key = os.getenv('MERCADO_PAGO_PUBLIC_KEY')

    print(f"Testing Mercado Pago Connection...")
    print(f"Access Token found: {'Yes' if access_token else 'No'}")
    print(f"Public Key found: {'Yes' if public_key else 'No'}")

    if not access_token:
        print("ERROR: MERCADO_PAGO_ACCESS_TOKEN not found in .env")
        return False

    sdk = mercadopago.SDK(access_token)

    # Cria uma preferência de teste simples
    preference_data = {
        "items": [
            {
                "title": "Test Item",
                "quantity": 1,
                "unit_price": 10.00,
                "currency_id": "BRL"
            }
        ],
        "payer": {
            "name": "Test",
            "surname": "User",
            "email": "test@user.com"
        },
        "back_urls": {
            "success": "http://localhost:8000/success",
            "failure": "http://localhost:8000/failure",
            "pending": "http://localhost:8000/pending"
        },
        # "auto_return": "approved",
    }

    try:
        # Teste simples de autenticação
        print("\nVerifying authentication with payment_methods()...")
        pm_response = sdk.payment_methods().list_all()
        if pm_response.get("status") == 200:
            print("Authentication OK (Payment methods listed)")
        else:
            print("Authentication verification failed or restricted scope.")
            print(f"Status: {pm_response.get('status')}")
            
        print("\nAttempting to create a preference again...")
        preference_response = sdk.preference().create(preference_data)
        
        response = preference_response.get("response", {})
        
        if "init_point" in response:
            print("SUCCESS: Preference created successfully!")
            print(f"Init Point: {response['init_point']}")
            return True
        else:
            print("FAILURE: Could not create preference.")
            print(f"Response Status: {preference_response.get('status')}")
            import json
            print(f"Full Response: {json.dumps(preference_response, indent=2)}")
            return False

    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_mercadopago_connection()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
