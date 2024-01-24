#!/usr/bin/env python
# encoding: utf-8
from fastapi import APIRouter
from cache import Cache

summaryRouter = APIRouter()


@summaryRouter.get("/all_markets")
def api_all_markets():
    return [k for k in Cache.markets_summary.values()]
