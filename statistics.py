#!/usr/bin/env python
# encoding: utf-8
import threading
import time
from decimal import Decimal

from cache import Asset, MarketSummary, Cache
from config import Application
from const import MarketStatusOpen
from crud import get_latest_traded_order, get_latest_24hour_volume, get_total_volume
from db import TMarket
from rpc import http_get_object, http_get_asset_imp


def market_statistics() -> None:
    while Application.statistics_thread_running:
        asset_idx = 0
        id2asset = {}
        symbol2asset = {}
        while Application.statistics_thread_running:
            asset_obj_id = "1.3.%d" % asset_idx
            res = http_get_object(Application.setting.API_URL, asset_obj_id)
            if len(res) == 1 and res[0] is None:
                break
            res = http_get_asset_imp(Application.setting.API_URL, res[0].get("symbol"))
            asset_id = res.get("id")
            symbol = res.get("symbol")
            precision = res.get("precision")
            max_supply = int(res.get("options").get("max_supply")) / (10 ** precision)
            current_supply = int(res.get("dynamic_data").get("current_supply")) / (10 ** precision)
            asset_idx = asset_idx + 1
            asset = Asset(asset_id=asset_id, symbol=symbol, precision=precision, max_supply=max_supply,
                          current_supply=current_supply)
            id2asset[asset_id] = asset
            symbol2asset[symbol] = asset

        balance_idx = 0
        symbol2holder = {}
        while Application.statistics_thread_running:
            balance_obj_id = "1.16.%d" % balance_idx
            res = http_get_object(Application.setting.API_URL, balance_obj_id)
            if len(res) == 1 and res[0] is None:
                break
            amount = int(res[0].get("balance").get("amount"))
            symbol = id2asset[res[0].get("balance").get("asset_id")].symbol
            if amount > 0:
                holders = symbol2holder.get(symbol)
                if holders is None:
                    symbol2holder[symbol] = 1
                else:
                    symbol2holder[symbol] = holders + 1
            balance_idx = balance_idx + 1

        markets_summary = {}
        if Application.statistics_thread_running:
            for r in TMarket.select().where(TMarket.market_status == MarketStatusOpen).execute():
                order = get_latest_traded_order(r.market_id)
                if order is not None:
                    price = (order.expect_buy_amount / Decimal(
                        10 ** symbol2asset[order.expect_buy_symbol].precision)) / (
                                    order.sell_amount / Decimal(10 ** symbol2asset[order.sell_symbol].precision))
                else:
                    price = Decimal(0.0)

                volume_latest_24hour = get_latest_24hour_volume(r.market_id)
                if volume_latest_24hour is not None:
                    volume_latest_24hour = volume_latest_24hour / Decimal(10 ** symbol2asset[r.quote_symbol].precision)
                else:
                    volume_latest_24hour = Decimal(0.0)

                volume_total = get_total_volume(r.market_id)
                if volume_total is not None:
                    volume_total = volume_total / Decimal(10 ** symbol2asset[r.quote_symbol].precision)
                else:
                    volume_total = Decimal(0.0)

                total_supply = Decimal(symbol2asset[r.base_symbol].current_supply) / Decimal(
                    10 ** symbol2asset[r.base_symbol].precision)

                market_cap = price * Decimal(symbol2asset[r.quote_symbol].current_supply) / Decimal(
                    10 ** symbol2asset[r.quote_symbol].precision)

                market_summary = MarketSummary(symbol=r.base_symbol, price=price,
                                               volume_latest_24hour=volume_latest_24hour,
                                               volume_total=volume_total, total_supply=total_supply,
                                               market_cap=market_cap, holders=symbol2holder.get(r.base_symbol))
                markets_summary[r.base_symbol] = market_summary

        if Application.statistics_thread_running:
            Cache.id2asset = id2asset
            Cache.symbol2asset = symbol2asset
            Cache.symbol2holder = symbol2holder
            Cache.markets_summary = markets_summary
            time.sleep(5)


def run_market_statistics_thread() -> None:
    Application.statistics_thread = threading.Thread(target=market_statistics, daemon=False)
    Application.statistics_thread_running = True
    Application.statistics_thread.start()
