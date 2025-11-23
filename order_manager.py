# order_manager.py
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, Tuple

from core_types import Order, ExecutionReport


class OrderManager:
    def __init__(
        self,
        starting_cash: float,
        max_orders_per_minute: int,
        max_long_position: int,
        max_short_position: int,
    ):
        self.cash = starting_cash
        self.max_orders_per_minute = max_orders_per_minute
        self.max_long_position = max_long_position
        self.max_short_position = max_short_position

        self.positions: Dict[str, int] = {}
        self._order_timestamps: deque[datetime] = deque()

    def _record_order_timestamp(self, now: datetime) -> None:
        self._order_timestamps.append(now)
        one_min_ago = now - timedelta(seconds=60)
        while self._order_timestamps and self._order_timestamps[0] < one_min_ago:
            self._order_timestamps.popleft()

    def _within_order_rate_limit(self, now: datetime) -> bool:
        self._record_order_timestamp(now)
        return len(self._order_timestamps) <= self.max_orders_per_minute

    def _position_after_order(self, order: Order) -> int:
        current = self.positions.get(order.symbol, 0)
        if order.side == "BUY":
            return current + order.quantity
        else:
            return current - order.quantity

    def _has_sufficient_capital(self, order: Order) -> bool:
        if order.side == "BUY":
            required = order.price * order.quantity
            return required <= self.cash
        return True

    def _within_position_limits(self, order: Order) -> bool:
        new_pos = self._position_after_order(order)
        if new_pos > self.max_long_position:
            return False
        if abs(min(new_pos, 0)) > self.max_short_position:
            return False
        return True

    def validate_order(self, order: Order, now: datetime | None = None) -> Tuple[bool, str]:
        if now is None:
            now = datetime.utcnow()

        if not self._within_order_rate_limit(now):
            return False, "Order rate limit exceeded"

        if not self._has_sufficient_capital(order):
            return False, "Insufficient capital"

        if not self._within_position_limits(order):
            return False, "Position limit exceeded"

        return True, "OK"

    def on_execution(self, report: ExecutionReport) -> None:
        if report.status not in ("FILLED", "PARTIALLY_FILLED"):
            return

        qty = report.filled_quantity
        if qty == 0:
            return

        notional = report.avg_price * qty
        pos = self.positions.get(report.symbol, 0)

        if report.side == "BUY":
            self.cash -= notional
            pos += qty
        else:
            self.cash += notional
            pos -= qty

        self.positions[report.symbol] = pos
