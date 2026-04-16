import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from ...src.domain.entities import Quote, QuoteStatus

def test_quote_is_expired_returns_true_when_past_expiration():
    # Arrange
    expires_at = datetime.now() - timedelta(seconds=1)
    quote = Quote(
        id=1,
        tenant_id="mesa-a",
        user_id=1,
        base_asset="BTC",
        quote_asset="BRL",
        side="BUY",
        volume=Decimal("0.5"),
        price_base=Decimal("350000"),
        price_final=Decimal("353500"),
        status=QuoteStatus.PENDING,
        created_at=datetime.now() - timedelta(minutes=1),
        expires_at=expires_at
    )
    
    # Act & Assert
    assert quote.is_expired() is True

def test_quote_is_expired_returns_false_when_future_expiration():
    # Arrange
    expires_at = datetime.now() + timedelta(seconds=30)
    quote = Quote(
        id=1,
        tenant_id="mesa-a",
        user_id=1,
        base_asset="BTC",
        quote_asset="BRL",
        side="BUY",
        volume=Decimal("0.5"),
        price_base=Decimal("350000"),
        price_final=Decimal("353500"),
        status=QuoteStatus.PENDING,
        created_at=datetime.now(),
        expires_at=expires_at
    )
    
    # Act & Assert
    assert quote.is_expired() is False
