import yfinance as yf
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from .models import TenantProfile, Quote, Trade
from core.multitenancy import get_current_tenant_id

class PricingService:
    """
    Fetches real-time prices and applies tenant-specific spreads.
    """
    
    @staticmethod
    def get_market_price(base_asset, quote_asset='BRL'):
        """
        Simulates fetching from an exchange using yfinance.
        For crypto, use tickers like 'BTC-BRL'.
        """
        symbol = f"{base_asset}-{quote_asset}"
        try:
            ticker = yf.Ticker(symbol)
            # Use fast_info or history to get current price
            price = ticker.fast_info['lastPrice']
            return Decimal(str(price))
        except Exception:
            # Fallback for mock/fail (returns dummy price)
            return Decimal('350000.00') if base_asset == 'BTC' else Decimal('1.00')

    @classmethod
    def get_quote_for_tenant(cls, tenant_slug, base_asset, volume, side):
        tenant = get_object_or_404(TenantProfile, tenant_slug=tenant_slug)
        
        market_price = cls.get_market_price(base_asset)
        spread = tenant.default_spread_percentage / 100
        
        if side == 'BUY':
            # Price is HIGHER for buyer
            final_price = market_price * (1 + spread)
        else:
            # Price is LOWER for seller
            final_price = market_price * (1 - spread)
            
        return {
            'market_price': market_price,
            'spread': tenant.default_spread_percentage,
            'final_price': final_price,
            'total_volume': volume
        }

class RFQService:
    """
    Handles the Request-for-Quote lifecycle.
    """
    
    @staticmethod
    def create_quote(user, base_asset, volume, side):
        tenant_id = get_current_tenant_id()
        if not tenant_id:
            raise ValueError("Tenant context not found")
            
        pricing = PricingService.get_quote_for_tenant(tenant_id, base_asset, volume, side)
        
        quote = Quote.objects.create(
            user=user,
            base_asset=base_asset,
            side=side,
            volume=volume,
            price_base=pricing['market_price'],
            spread_applied=pricing['spread'],
            price_final=pricing['final_price'],
            status='P',
            expires_at=timezone.now() + timedelta(seconds=30) # 30s lock
        )
        return quote

    @staticmethod
    def execute_trade(quote_id, user):
        quote = get_object_or_404(Quote, id=quote_id, user=user, status='P')
        
        if quote.expires_at < timezone.now():
            quote.status = 'E'
            quote.save()
            raise ValueError("Quote expired")
            
        trade = Trade.objects.create(
            quote=quote,
            user=user,
            final_price=quote.price_final,
            total_volume=quote.volume,
            total_quote=quote.volume * quote.price_final
        )
        
        quote.status = 'A'
        quote.save()
        
        return trade
