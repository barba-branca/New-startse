# import yfinance as yf # Temporarily disabled due to OS App Control policy blocking DLLs
from decimal import Decimal
from typing import Optional
from ...domain.entities import IPriceProvider

class YFinancePriceProvider(IPriceProvider):
    """
    Mock Price Provider to bypass system security restrictions.
    Returns static prices for development and UI testing.
    """
    def __init__(self):
        # self.ticker = yf.Ticker("BTC-USD")
        pass
        
    def get_last_price(self, asset: str, currency: str) -> Decimal:
        # Mock logic: Return fixed prices
        # asset is expected as 'BTC' or 'ETH'
        mock_prices = {
            "BTC": Decimal("350000.00"),
            "ETH": Decimal("15000.00"),
            "USD": Decimal("5.50")
        }
        return mock_prices.get(asset.upper(), Decimal("100.00"))

class DefaultSpreadStrategy:
    """
    Standard implementation of spread calculation.
    """
    def calculate_price(self, market_price: Decimal, side: str, tenant) -> Decimal:
        spread = tenant.default_spread / Decimal('100')
        if side.upper() == 'BUY':
            return market_price * (1 + spread)
        return market_price * (1 - spread)
