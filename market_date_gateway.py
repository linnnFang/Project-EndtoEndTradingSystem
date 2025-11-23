# market_data_gateway.py
from typing import Iterator, Optional, Tuple
from datetime import datetime

import pandas as pd


class MarketDataGateway:
    def __init__(self, csv_path: str):
        self.data = pd.read_csv(csv_path, parse_dates=["Datetime"])
        self.data.set_index("Datetime", inplace=True)
        self.data.sort_index(inplace=True)
        self._cursor = 0
        self._index = self.data.index

    def reset(self) -> None:
        self._cursor = 0

    def get_next_tick(self) -> Optional[Tuple[datetime, pd.Series]]:
        if self._cursor >= len(self.data):
            return None
        idx = self._index[self._cursor]
        row = self.data.iloc[self._cursor]
        self._cursor += 1
        return idx.to_pydatetime(), row

    def iter_ticks(self) -> Iterator[Tuple[datetime, pd.Series]]:
        self.reset()
        while True:
            tick = self.get_next_tick()
            if tick is None:
                break
            yield tick
