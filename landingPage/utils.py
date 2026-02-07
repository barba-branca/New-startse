import yfinance as yf
import cachetools.func
import mercadopago
from django.conf import settings

@cachetools.func.ttl_cache(maxsize=128, ttl=600)  # Cache por 10 minutos
def get_b3_data():
    """
    Busca dados das principais empresas da B3.
    """
    tickers = {
        '^BVSP': 'Ibovespa',
        'PETR4.SA': 'Petrobras',
        'VALE3.SA': 'Vale',
        'ITUB4.SA': 'Itaú Unibanco',
        'BBDC4.SA': 'Bradesco',
        'ABEV3.SA': 'Ambev'
    }
    
    data = []
    for ticker, name in tickers.items():
        try:
            t = yf.Ticker(ticker)
            # Pegamos o histórico recente para cotação
            info = t.history(period='1d')
            if not info.empty:
                current_price = info['Close'].iloc[-1]
                # Para variação, usamos o anterior (aproximado)
                prev_close = info['Open'].iloc[-1]
                change = current_price - prev_close
                pct_change = (change / prev_close) * 100
                
                # Capitalização de Mercado (Market Cap)
                market_cap = t.info.get('marketCap', 0)
                if market_cap > 1_000_000_000_000:
                    market_cap_str = f"R$ {market_cap / 1_000_000_000_000:.1f}T"
                elif market_cap > 1_000_000_000:
                    market_cap_str = f"R$ {market_cap / 1_000_000_000:.1f}B"
                elif market_cap > 1_000_000:
                    market_cap_str = f"R$ {market_cap / 1_000_000:.1f}M"
                else:
                    market_cap_str = f"R$ {market_cap}"

                data.append({
                    'symbol': ticker.replace('.SA', '').replace('^', ''),
                    'name': name,
                    'price': round(current_price, 2),
                    'change': round(change, 2),
                    'pct_change': round(pct_change, 2),
                    'positive': change >= 0,
                    'market_cap': market_cap_str
                })
        except Exception as e:
            print(f"Erro ao buscar dados de {ticker}: {e}")
            
    return data

def create_checkout_preference(user, plan_name, price):
    """
    Cria uma preferência de pagamento no Mercado Pago.
    """
    if not settings.MERCADO_PAGO_ACCESS_TOKEN:
        print("MERCADO_PAGO_ACCESS_TOKEN não configurado")
        return None

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
            "name": user.first_name,
            "surname": user.last_name,
            "email": user.email,
        },
        "back_urls": {
            "success": "https://new-start-se-e9ctbxanc2hufze3.canadacentral-01.azurewebsites.net/empresarios/cadastrar_empresa/",
            "failure": "https://new-start-se-e9ctbxanc2hufze3.canadacentral-01.azurewebsites.net/?status=failure",
            "pending": "https://new-start-se-e9ctbxanc2hufze3.canadacentral-01.azurewebsites.net/?status=pending"
        },
        "auto_return": "approved",
    }
    
    preference_response = sdk.preference().create(preference_data)
    
    if "response" in preference_response:
        return preference_response["response"]["init_point"]
    return None
