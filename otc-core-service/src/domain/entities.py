from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

class QuoteStatus(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

@dataclass
class TenantContext:
    tenant_id: str
    name: str
    default_spread: Decimal

@dataclass
class Quote:
    id: Optional[int]
    tenant_id: str
    user_id: int
    base_asset: str
    quote_asset: str
    side: str
    volume: Decimal
    price_base: Decimal
    price_final: Decimal
    status: QuoteStatus
    created_at: datetime
    expires_at: datetime

    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

@dataclass
class Trade:
    id: Optional[int]
    quote_id: int
    tenant_id: str
    user_id: int
    final_price: Decimal
    total_volume: Decimal
    executed_at: datetime
