# matching_engine.py
from datetime import datetime
from typing import Optional
import random

from core_types import Order, ExecutionReport


class MatchingEngine:
    def __init__(
        self,
        fill_probability: float = 0.6,
        partial_fill_probability: float = 0.25,
        seed: Optional[int] = None,
    ):
        if seed is not None:
            random.seed(seed)

        self.fill_probability = fill_probability
        self.partial_fill_probability = partial_fill_probability

    def process_order(self, order: Order, timestamp: Optional[datetime] = None) -> ExecutionReport:
        if timestamp is None:
            timestamp = datetime.utcnow()

        r = random.random()

        if r < self.fill_probability:
            status = "FILLED"
            filled_qty = order.quantity
            remaining = 0
        elif r < self.fill_probability + self.partial_fill_probability and order.quantity > 1:
            status = "PARTIALLY_FILLED"
            filled_qty = random.randint(1, order.quantity - 1)
            remaining = order.quantity - filled_qty
        else:
            status = "CANCELLED"
            filled_qty = 0
            remaining = order.quantity

        avg_price = order.price if filled_qty > 0 else 0.0

        return ExecutionReport(
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            status=status,
            filled_quantity=filled_qty,
            remaining_quantity=remaining,
            avg_price=avg_price,
            timestamp=timestamp,
        )
