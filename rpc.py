#!/usr/bin/env python
# encoding: utf-8

import requests  # type: ignore


def http_get_block_height(url):
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "info",
        "params": [],
    }
    resp = requests.post(url=url, json=payload)
    return resp.json().get("result").get("head_block_num")
