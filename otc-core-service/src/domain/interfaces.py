from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, List
from .entities import Quote, Trade, TenantContext

class IPriceProvider(ABC):
    """ Interface for fetching market prices from External Liquidity Providers """
    @abstractmethod
    def get_last_price(self, base_asset: str, quote_asset: str) -> Decimal:
        pass

class ISpreadStrategy(ABC):
    """ Strategy for calculating spreads based on Tenant-specific rules """
    @abstractmethod
    def calculate_price(self, market_price: Decimal, side: str, tenant: TenantContext) -> Decimal:
        pass

class IOTCRepository(ABC):
    """ Repository for persisting Quotes and Trades (Framework Agnostic) """
    @abstractmethod
    def save_quote(self, quote: Quote) -> Quote:
        pass

    @abstractmethod
    def get_quote_by_id(self, quote_id: int) -> Optional[Quote]:
        pass

    @abstractmethod
    def save_trade(self, trade: Trade) -> Trade:
        pass

    @abstractmethod
    def get_tenant_profile(self, tenant_id: str) -> Optional[TenantContext]:
        pass

class IKYCService(ABC):
    """ Interface for User Validation (Separation of Responsibilities) """
    @abstractmethod
    def is_user_eligible(self, user_id: int, tenant_id: str) -> bool:
        pass
