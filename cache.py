#!/usr/bin/env python
# encoding: utf-8
from decimal import Decimal
from typing import Dict


class Asset(object):
    def __init__(self, asset_id: str, symbol: str, precision: int, max_supply: int, current_supply: int):
        self.id = asset_id
        self.symbol = symbol
        self.precision = precision
        self.max_supply = max_supply
        self.current_supply = current_supply


class MarketSummary(object):
    def __init__(self, symbol: str, market_id: str, market_name: str, price: Decimal, volume_latest_24hour: Decimal,
                 volume_total: Decimal, total_supply: Decimal, market_cap: Decimal, holders: int):
        self.symbol = symbol
        self.market_id = market_id
        self.market_name = market_name
        self.price = "%.08f" % price
        self.volume_latest_24hour = "%.08f" % volume_latest_24hour
        self.volume_total = "%.08f" % volume_total
        self.total_supply = "%.08f" % total_supply
        self.market_cap = "%.08f" % market_cap
        self.holders = holders


class Cache(object):
    id2asset: Dict = {}
    symbol2asset: Dict = {}
    symbol2holder: Dict = {}
    markets_summary: Dict = {}
