#!/usr/bin/env python
# encoding: utf-8
from datetime import datetime


def utc_time_str_to_datetime(utc_time_str: str) -> datetime:
    return datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%S')
