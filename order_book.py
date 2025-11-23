# order_book.py
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import heapq

from core_types import Order, Trade


class OrderBook:
    def __init__(self):
        self.bids: List[Tuple[float, float, int, Order]] = []
        self.asks: List[Tuple[float, float, int, Order]] = []
        self.order_index: Dict[int, Order] = {}
        self._next_order_id = 1

    def _next_id(self) -> int:
        oid = self._next_order_id
        self._next_order_id += 1
        return oid

    def create_order(self, symbol: str, side: str, price: float,
                     quantity: int, timestamp: Optional[datetime] = None) -> Order:
        if timestamp is None:
            timestamp = datetime.utcnow()
        return Order(
            order_id=self._next_id(),
            symbol=symbol,
            side=side.upper(),
            price=price,
            quantity=quantity,
            timestamp=timestamp,
        )

    def add_order(self, order: Order) -> List[Trade]:
        trades: List[Trade] = []
        if order.side not in ("BUY", "SELL"):
            raise ValueError("side must be 'BUY' or 'SELL'")

        if order.side == "BUY":
            opp_book = self.asks

            def is_matchable(opp_price: float) -> bool:
                return order.price >= opp_price
        else:
            opp_book = self.bids

            def is_matchable(opp_price: float) -> bool:
                return order.price <= opp_price

        while order.remaining > 0 and opp_book:
            price_key, ts, oid, resting = opp_book[0]

            if (not resting.active) or resting.remaining <= 0:
                heapq.heappop(opp_book)
                continue

            if resting.side == "BUY":
                opp_price = -price_key
            else:
                opp_price = price_key

            if not is_matchable(opp_price):
                break

            heapq.heappop(opp_book)

            trade_qty = min(order.remaining, resting.remaining)
            trade_price = opp_price
            trade_time = max(order.timestamp, resting.timestamp)

            if order.side == "BUY":
                buy_order, sell_order = order, resting
            else:
                buy_order, sell_order = resting, order

            trades.append(
                Trade(
                    buy_order_id=buy_order.order_id,
                    sell_order_id=sell_order.order_id,
                    symbol=order.symbol,
                    price=trade_price,
                    quantity=trade_qty,
                    timestamp=trade_time,
                )
            )

            order.remaining -= trade_qty
            resting.remaining -= trade_qty

            if resting.remaining > 0:
                if resting.side == "BUY":
                    heapq.heappush(self.bids, (-resting.price, ts, resting.order_id, resting))
                else:
                    heapq.heappush(self.asks, (resting.price, ts, resting.order_id, resting))
            else:
                resting.active = False

        if order.remaining > 0:
            self.order_index[order.order_id] = order
            ts = order.timestamp.timestamp()
            if order.side == "BUY":
                heapq.heappush(self.bids, (-order.price, ts, order.order_id, order))
            else:
                heapq.heappush(self.asks, (order.price, ts, order.order_id, order))

        return trades

    def cancel_order(self, order_id: int) -> bool:
        order = self.order_index.get(order_id)
        if not order or not order.active:
            return False
        order.active = False
        order.remaining = 0
        return True

    def modify_order(self, order_id: int,
                     new_price: Optional[float] = None,
                     new_quantity: Optional[int] = None,
                     timestamp: Optional[datetime] = None) -> Optional[Order]:
        order = self.order_index.get(order_id)
        if not order or not order.active:
            return None

        self.cancel_order(order_id)

        if timestamp is None:
            timestamp = datetime.utcnow()

        updated_price = new_price if new_price is not None else order.price
        updated_qty = new_quantity if new_quantity is not None else order.quantity

        new_order = Order(
            order_id=order_id,
            symbol=order.symbol,
            side=order.side,
            price=updated_price,
            quantity=updated_qty,
            timestamp=timestamp,
        )
        self.order_index[order_id] = new_order
        self.add_order(new_order)
        return new_order

    def top_of_book(self, symbol: str) -> Tuple[Optional[float], Optional[float]]:
        best_bid, best_ask = None, None

        for price_key, ts, oid, order in self.bids:
            if order.active and order.symbol == symbol and order.remaining > 0:
                best_bid = -price_key
                break

        for price_key, ts, oid, order in self.asks:
            if order.active and order.symbol == symbol and order.remaining > 0:
                best_ask = price_key
                break

        return best_bid, best_ask
