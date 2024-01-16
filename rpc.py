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


def http_get_block(url, height):
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "get_block",
        "params": [height, ],
    }
    resp = requests.post(url=url, json=payload)
    return resp.json().get("result")


def http_get_block_all_tx_hash(url, height):
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "get_block",
        "params": [height, ],
    }
    resp = requests.post(url=url, json=payload)
    return resp.json().get("result").get("transaction_ids")


def http_get_transaction_by_hash(url, tx_hash):
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "get_transaction",
        "params": [tx_hash, ],
    }
    resp = requests.post(url=url, json=payload)
    return resp.json().get("result")


def http_get_contract_invoke_object(url, tx_hash):
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "get_contract_invoke_object",
        "params": [tx_hash, ],
    }
    resp = requests.post(url=url, json=payload)
    return resp.json().get("result")
