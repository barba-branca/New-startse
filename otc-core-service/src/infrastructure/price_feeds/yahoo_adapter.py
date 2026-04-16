import yfinance as yf
from decimal import Decimal
from ...domain.interfaces import IPriceProvider

class YahooFinanceProvider(IPriceProvider):
    """
    Adapter for Yahoo Finance. 
    Implements IPriceProvider (Infrastructure Layer).
    """
    
    def get_last_price(self, base_asset: str, quote_asset: str) -> Decimal:
        symbol = f"{base_asset.upper()}-{quote_asset.upper()}"
        try:
            # Note: In a real high-perf scenario, we would add Circuit Breaker here
            ticker = yf.Ticker(symbol)
            price = ticker.fast_info['lastPrice']
            return Decimal(str(price))
        except Exception as e:
            # Fallback for internal simulator or error handling
            raise Exception(f"Liquidity Provider Offline: {str(e)}")

class DefaultSpreadStrategy:
    """
    Standard implementation of spread calculation.
    """
    def calculate_price(self, market_price: Decimal, side: str, tenant) -> Decimal:
        spread = tenant.default_spread / Decimal('100')
        if side.upper() == 'BUY':
            return market_price * (1 + spread)
        return market_price * (1 - spread)
