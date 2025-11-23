# core_types.py
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Order:
    order_id: int
    symbol: str
    side: str      # 'BUY' or 'SELL'
    price: float
    quantity: int
    timestamp: datetime
    remaining: int = field(init=False)
    active: bool = field(default=True)

    def __post_init__(self):
        self.remaining = self.quantity


@dataclass
class Trade:
    buy_order_id: int
    sell_order_id: int
    symbol: str
    price: float
    quantity: int
    timestamp: datetime


@dataclass
class ExecutionReport:
    order_id: int
    symbol: str
    side: str
    status: str            # 'NEW', 'FILLED', ...
    filled_quantity: int
    remaining_quantity: int
    avg_price: float
    timestamp: datetime
