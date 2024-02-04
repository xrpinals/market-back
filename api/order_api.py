#!/usr/bin/env python
# encoding: utf-8
from fastapi import APIRouter
from playhouse.shortcuts import model_to_dict  # type: ignore

from db import TOrder
from model import OrderQuery, OrderAsc

orderRouter = APIRouter()


@orderRouter.post("/query_orders")
def api_query_orders(query: OrderQuery):
    scheme = TOrder.select()

    if query.market_id is not None and len(query.market_id) != 0:
        query.market_id = query.market_id.lstrip().rstrip()
        scheme = scheme.where(TOrder.market_id == query.market_id)

    if query.seller is not None and len(query.seller) != 0:
        query.seller = query.seller.lstrip().rstrip()
        scheme = scheme.where(TOrder.seller == query.seller)

    if len(query.status) != 0:
        scheme = scheme.where(TOrder.order_status.in_(query.status))

    if query.order_by == "price":
        if query.order == OrderAsc:
            scheme = scheme.order_by((TOrder.expect_buy_amount / TOrder.sell_amount).asc())
        else:
            scheme = scheme.order_by((TOrder.expect_buy_amount / TOrder.sell_amount).desc())
    elif query.order_by == "placed_time":
        if query.order == OrderAsc:
            scheme = scheme.order_by(TOrder.order_placed_datetime.asc())
        else:
            scheme = scheme.order_by(TOrder.order_placed_datetime.desc())

    total_count = scheme.count()
    scheme = scheme.offset(query.offset).limit(query.limit)
    return dict(data=dict(total_count=total_count, result=[model_to_dict(r) for r in scheme.execute()]), retCode=200,
                retMsg="")
