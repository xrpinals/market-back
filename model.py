#!/usr/bin/env python
# encoding: utf-8
from typing import Optional

import pydantic
from pydantic import BaseModel, Field

OrderAsc = 0
OrderDesc = 1


class PageArgsQuery(BaseModel):
    offset: int = Field(default=0, ge=0, description="offset should >= 0")
    limit: int = Field(default=10, ge=0, description="limit should >= 0")


class OrderQuery(PageArgsQuery):
    market_id: Optional[str] = Field(default=None)
    seller: Optional[str] = Field(default=None)
    status: list[int]
    order_by: str
    # 0: asc
    # 1: desc (default)
    order: int = Field(ge=OrderAsc, le=OrderDesc, description="order should >=0 && <=1")

    @pydantic.validator("order_by")
    def check_order_by(cls, v):
        if v not in ("price", "placed_time"):
            raise ValueError("invalid order_by")
        return v
