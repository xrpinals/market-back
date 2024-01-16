#!/usr/bin/env python
# encoding: utf-8

from db import *


def query_next_consume_height() -> TGlobal:
    return TGlobal.get_or_none(TGlobal.variate == "next_consume_height")


def update_next_consume_height(height) -> None:
    TGlobal.update(value=str(height)).where(TGlobal.variate == "next_consume_height").execute()
