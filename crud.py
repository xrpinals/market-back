#!/usr/bin/env python
# encoding: utf-8
from datetime import datetime
from typing import Optional
from decimal import Decimal

from const import MarketStatusOpen, MarketStatusClosed, OrderStatusPlaced, OrderStatusCanceled, OrderStatusExchanged
from db import *


def query_next_consume_height() -> Optional[TGlobal]:
    return TGlobal.get_or_none(TGlobal.variate == "next_consume_height")


def update_next_consume_height(height: int) -> None:
    TGlobal.update(value=str(height)).where(TGlobal.variate == "next_consume_height").execute()


def insert_new_market(market_id: str, owner: str, create_height: int, create_datetime: datetime) -> None:
    TMarket.insert(market_id=market_id, owner=owner, market_create_height=create_height,
                   market_create_datetime=create_datetime, market_status=MarketStatusClosed).execute()


def open_market(market_id: str, market_name: str, base_symbol: str, quote_symbol: str) -> None:
    TMarket.update(market_name=market_name, base_symbol=base_symbol, quote_symbol=quote_symbol,
                   market_status=MarketStatusOpen).where(
        TMarket.market_id == market_id, TMarket.market_status == MarketStatusClosed).execute()


def update_market_status(market_id: str, old_market_status: int, new_market_status: int) -> None:
    TMarket.update(market_status=new_market_status).where(TMarket.market_id == market_id,
                                                          TMarket.market_status == old_market_status).execute()


def cancel_order(market_id: str, order_idx: int) -> None:
    TOrder.update(order_status=OrderStatusCanceled).where(TOrder.market_id == market_id, TOrder.order_idx == order_idx,
                                                          TOrder.order_status == OrderStatusPlaced).execute()


def insert_new_order(market_id: str, order_idx: int, seller: str, sell_symbol: str, sell_amount: Decimal,
                     expect_buy_symbol: str,
                     expect_buy_amount: Decimal, order_placed_tx: str, order_placed_height: int,
                     order_placed_datetime: datetime) -> None:
    TOrder.insert(market_id=market_id, order_idx=order_idx, seller=seller, sell_symbol=sell_symbol,
                  sell_amount=sell_amount, expect_buy_symbol=expect_buy_symbol, expect_buy_amount=expect_buy_amount,
                  order_placed_tx=order_placed_tx, order_placed_height=order_placed_height,
                  order_placed_datetime=order_placed_datetime, order_status=OrderStatusPlaced).execute()


def exchange_order(market_id: str, order_idx: int, trade_tx: str, buyer: str, fee: Decimal, trade_height: int,
                   trade_datetime: datetime) -> None:
    TOrder.update(trade_tx=trade_tx, buyer=buyer, fee=fee, trade_height=trade_height, trade_datetime=trade_datetime,
                  order_status=OrderStatusExchanged).where(TOrder.market_id == market_id, TOrder.order_idx == order_idx,
                                                           TOrder.order_status == OrderStatusPlaced).execute()
