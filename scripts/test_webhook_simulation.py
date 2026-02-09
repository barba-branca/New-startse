import os
import sys
import json
import django
from unittest.mock import MagicMock, patch
from django.test import RequestFactory

# Setup Django environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from landingPage.views import webhook_mercadopago

def test_webhook():
    print("Simulating Mercado Pago Webhook...")
    
    # Mocking Mercado Pago SDK
    with patch('mercadopago.SDK') as MockSDK:
        # Configura o mock
        mock_instance = MockSDK.return_value
        mock_payment = mock_instance.payment.return_value
        
        # Simula resposta de pagamento aprovado
        mock_payment.get.return_value = {
            "status": 200,
            "response": {
                "status": "approved",
                "id": 123456789,
                "external_reference": "user_123"
            }
        }

        # Cria uma request POST simulada
        factory = RequestFactory()
        data = {'type': 'payment', 'data': {'id': '123456789'}}
        request = factory.post(
            '/webhooks/mercadopago/?topic=payment&id=123456789',
            data=json.dumps(data),
            content_type='application/json'
        )

        # Chama a view
        response = webhook_mercadopago(request)

        print(f"Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: Webhook handled successfully.")
        else:
            print("FAILURE: Webhook returned unexpected status.")

if __name__ == "__main__":
    test_webhook()
