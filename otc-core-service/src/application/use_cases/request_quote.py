from datetime import datetime, timedelta
from decimal import Decimal
from ..domain.entities import Quote, QuoteStatus
from ..domain.interfaces import IPriceProvider, IOTCRepository, ISpreadStrategy, IKYCService

class RequestQuoteUseCase:
    """
    Use Case: Client requests a fixed price for an asset (RFQ).
    Follows Clean Architecture by depending only on abstractions.
    """
    
    def __init__(
        self, 
        repository: IOTCRepository,
        price_provider: IPriceProvider,
        spread_strategy: ISpreadStrategy,
        kyc_service: IKYCService
    ):
        self.repository = repository
        self.price_provider = price_provider
        self.spread_strategy = spread_strategy
        self.kyc_service = kyc_service

    def execute(self, tenant_id: str, user_id: int, asset: str, volume: Decimal, side: str) -> Quote:
        # 1. Responsibility Split: Validate KYC first
        if not self.kyc_service.is_user_eligible(user_id, tenant_id):
            raise Exception("User not eligible for OTC trading (KYC failing).")
            
        # 2. Get Tenant Context
        tenant = self.repository.get_tenant_profile(tenant_id)
        if not tenant:
            raise Exception(f"Tenant {tenant_id} not found.")

        # 3. Fetch Market Price (DIP: calling interface)
        market_price = self.price_provider.get_last_price(asset, "BRL")
        
        # 4. Apply Spread Strategy (Strategy Pattern)
        final_price = self.spread_strategy.calculate_price(market_price, side, tenant)
        
        # 5. Create Quote with 30s TTL
        quote = Quote(
            id=None,
            tenant_id=tenant_id,
            user_id=user_id,
            base_asset=asset,
            quote_asset="BRL",
            side=side,
            volume=volume,
            price_base=market_price,
            price_final=final_price,
            status=QuoteStatus.PENDING,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=30)
        )
        
        # 6. Persistence
        return self.repository.save_quote(quote)
