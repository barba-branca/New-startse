from ...domain.entities import Quote, Trade, TenantContext, QuoteStatus
from ...domain.interfaces import IOTCRepository
from otc.models import Quote as DjangoQuote, Trade as DjangoTrade, TenantProfile
from django.utils import timezone
from decimal import Decimal

class DjangoOTCRepository(IOTCRepository):
    """
    Adapter that bridges the Domain with the Django ORM.
    Ensures the business logic remains agnostic of models.py.
    """

    def save_quote(self, quote: Quote) -> Quote:
        # Map Domain Entity to Django Model
        dj_quote = DjangoQuote.objects.create(
            tenant_id=quote.tenant_id,
            user_id=quote.user_id,
            base_asset=quote.base_asset,
            quote_asset=quote.quote_asset,
            side=quote.side,
            volume=quote.volume,
            price_base=quote.price_base,
            price_final=quote.price_final,
            status=quote.status.value,
            expires_at=quote.expires_at
        )
        quote.id = dj_quote.id
        return quote

    def get_tenant_profile(self, tenant_id: str) -> Optional[TenantContext]:
        try:
            profile = TenantProfile.objects.get(tenant_slug=tenant_id)
            return TenantContext(
                tenant_id=profile.tenant_slug,
                name=profile.name,
                default_spread=profile.default_spread_percentage
            )
        except TenantProfile.DoesNotExist:
            return None

    def save_trade(self, trade: Trade) -> Trade:
        # Implementation for saving trade...
        pass

    def get_quote_by_id(self, quote_id: int) -> Optional[Quote]:
        # Mapping back to Domain...
        pass
