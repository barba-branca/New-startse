import pytest
from unittest.mock import MagicMock
from decimal import Decimal
from ...src.application.use_cases.request_quote import RequestQuoteUseCase
from ...src.domain.entities import TenantContext, Quote

def test_request_quote_creates_quote_successfully():
    # Arrange
    mock_repo = MagicMock()
    mock_price_provider = MagicMock()
    mock_spread_strategy = MagicMock()
    mock_kyc = MagicMock()
    
    tenant = TenantContext(tenant_id="mesa-a", name="Mesa A", default_spread=Decimal("1.0"))
    
    mock_kyc.is_user_eligible.return_value = True
    mock_repo.get_tenant_profile.return_value = tenant
    mock_price_provider.get_last_price.return_value = Decimal("350000")
    mock_spread_strategy.calculate_price.return_value = Decimal("353500")
    
    # Configure repo.save_quote to return the quote passed to it
    def save_side_effect(quote):
        quote.id = 999
        return quote
    mock_repo.save_quote.side_effect = save_side_effect
    
    use_case = RequestQuoteUseCase(
        repository=mock_repo,
        price_provider=mock_price_provider,
        spread_strategy=mock_spread_strategy,
        kyc_service=mock_kyc
    )
    
    # Act
    quote = use_case.execute(
        tenant_id="mesa-a",
        user_id=1,
        asset="BTC",
        volume=Decimal("0.1"),
        side="BUY"
    )
    
    # Assert
    assert quote.id == 999
    assert quote.price_final == Decimal("353500")
    assert quote.tenant_id == "mesa-a"
    mock_kyc.is_user_eligible.assert_called_once()
    mock_repo.save_quote.assert_called_once()

def test_request_quote_fails_if_kyc_not_eligible():
    # Arrange
    mock_kyc = MagicMock()
    mock_kyc.is_user_eligible.return_value = False
    
    use_case = RequestQuoteUseCase(
        repository=MagicMock(),
        price_provider=MagicMock(),
        spread_strategy=MagicMock(),
        kyc_service=mock_kyc
    )
    
    # Act & Assert
    with pytest.raises(Exception, match="User not eligible"):
        use_case.execute("mesa-a", 1, "BTC", Decimal("0.1"), "BUY")
