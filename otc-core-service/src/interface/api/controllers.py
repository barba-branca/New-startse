from ...application.use_cases.request_quote import RequestQuoteUseCase
from ...infrastructure.persistence.django_adapter import DjangoOTCRepository
from ...infrastructure.price_feeds.yahoo_adapter import YahooFinanceProvider, DefaultSpreadStrategy
from ...infrastructure.circuit_breaker import CircuitBreaker
from decimal import Decimal

# Dependency Injection Setup (Composition Root)
# This is where we wire everything together.
_repo = DjangoOTCRepository()
_price_provider = YahooFinanceProvider()
_spread_strategy = DefaultSpreadStrategy()
_breaker = CircuitBreaker()

class RFQController:
    """
    Controller for RFQ operations. 
    Can be called by FastAPI, Django Views, or MCP Tools.
    """
    
    @staticmethod
    def handle_request_quote(tenant_id: str, user_id: int, asset: str, volume: float, side: str):
        use_case = RequestQuoteUseCase(
            repository=_repo,
            price_provider=_price_provider,
            spread_strategy=_spread_strategy,
            kyc_service=None # Needs implementation
        )
        
        # Wrapped in circuit breaker for infra resiliency
        quote = _breaker.call(
            use_case.execute,
            tenant_id=tenant_id,
            user_id=user_id,
            asset=asset,
            volume=Decimal(str(volume)),
            side=side
        )
        
        return {
            "id": quote.id,
            "asset": quote.base_asset,
            "price": float(quote.price_final),
            "total": float(quote.price_final * quote.volume),
            "expires_at": quote.expires_at.isoformat(),
            "status": "PENDING"
        }

# MCP TOOL SPECIFICATION (JSON Schema format)
MCP_TOOLS = [
    {
        "name": "otc_request_quote",
        "description": "Requests a fixed price quote for an OTC trade (RFQ). Valid for 30s.",
        "input_schema": {
            "type": "object",
            "properties": {
                "asset": {"type": "string", "description": "Asset ticker (e.g. BTC)"},
                "volume": {"type": "number", "description": "Amount to buy/sell"},
                "side": {"type": "string", "enum": ["BUY", "SELL"]}
            },
            "required": ["asset", "volume", "side"]
        }
    }
]
