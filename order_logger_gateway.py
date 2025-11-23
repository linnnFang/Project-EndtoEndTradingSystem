# order_logger_gateway.py
import csv
from datetime import datetime
from typing import Optional

from core_types import Order


class OrderLoggerGateway:
    def __init__(self, log_path: str):
        self.log_path = log_path
        with open(self.log_path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "timestamp",
                    "event_type",
                    "order_id",
                    "symbol",
                    "side",
                    "price",
                    "quantity",
                    "info",
                ]
            )

    def log_order_event(
        self,
        event_type: str,
        order: Optional[Order] = None,
        info: str = "",
        timestamp: Optional[datetime] = None,
    ) -> None:
        if timestamp is None:
            timestamp = datetime.utcnow()

        row = {
            "timestamp": timestamp.isoformat(),
            "event_type": event_type,
            "order_id": getattr(order, "order_id", None),
            "symbol": getattr(order, "symbol", None),
            "side": getattr(order, "side", None),
            "price": getattr(order, "price", None),
            "quantity": getattr(order, "quantity", None),
            "info": info,
        }

        with open(self.log_path, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    row["timestamp"],
                    row["event_type"],
                    row["order_id"],
                    row["symbol"],
                    row["side"],
                    row["price"],
                    row["quantity"],
                    row["info"],
                ]
            )
