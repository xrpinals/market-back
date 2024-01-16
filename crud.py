#!/usr/bin/env python
# encoding: utf-8
from datetime import datetime
from typing import Optional

from db import *


def query_next_consume_height() -> Optional[TGlobal]:
    return TGlobal.get_or_none(TGlobal.variate == "next_consume_height")


def update_next_consume_height(height) -> None:
    TGlobal.update(value=str(height)).where(TGlobal.variate == "next_consume_height").execute()


def query_market_state_by_creater(creater: str) -> Optional[TMarketState]:
    return TMarketState.get_or_none(TMarketState.creater == creater)


def query_market_state_by_market_id(market_id: str) -> Optional[TMarketState]:
    return TMarketState.get_or_none(TMarketState.market_id == market_id)


def insert_market_state(market_id: str, creater: str, create_height: int, state_timestamp: datetime) -> None:
    TMarketState.insert(market_id=market_id, creater=creater,
                        create_height=create_height,
                        state_orders="[]", state_height=create_height,
                        state_timestamp=state_timestamp, created_at=datetime.now(),
                        updated_at=datetime.now()).execute()
