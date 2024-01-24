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
    def __init__(self, symbol: str, price: Decimal, volume_latest_24hour: Decimal, volume_total: Decimal,
                 total_supply: Decimal, market_cap: Decimal, holders: int):
        self.symbol = symbol
        self.price = price
        self.volume_latest_24hour = volume_latest_24hour
        self.volume_total = volume_total
        self.total_supply = total_supply
        self.market_cap = market_cap
        self.holders = holders


class Cache(object):
    id2asset: Dict = {}
    symbol2asset: Dict = {}
    symbol2holder: Dict = {}
    markets_summary: Dict = {}
