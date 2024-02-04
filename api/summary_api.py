#!/usr/bin/env python
# encoding: utf-8
from fastapi import APIRouter
from cache import Cache

summaryRouter = APIRouter()


@summaryRouter.get("/all_markets")
def api_all_markets():
    return dict(data=[k for k in Cache.markets_summary.values()], retCode=200, retMsg="")
