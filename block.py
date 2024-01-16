#!/usr/bin/env python
# encoding: utf-8
import json
import threading
import time
from typing import Dict

from crud import *
from rpc import *
from utils import *
from config import Application
from enum import IntEnum


class TxType(IntEnum):
    TxTypeContractRegister = 1
    TxTypeContractInvoke = 2
    TxTypeOther = 3


def parse_tx_type(tx) -> TxType:
    for op in tx.get("operations"):
        if op[0] == TxType.TxTypeContractRegister.value:
            return TxType.TxTypeContractRegister
        elif op[0] == TxType.TxTypeContractInvoke.value:
            return TxType.TxTypeContractInvoke
    return TxType.TxTypeOther


def parse_tx_contract_register_result(tx_receipt) -> (bool, Optional[str], Optional[str]):
    for obj in tx_receipt:
        if obj.get("exec_succeed"):
            return True, obj.get("invoker"), obj.get("contract_registed")
    return False, None, None


def parse_tx_contract_invoke_result(tx_receipt) -> (bool, Optional[str], list):
    for obj in tx_receipt:
        if obj.get("exec_succeed"):
            return True, obj.get("invoker"), obj.get("events")
    return False, None, None


def parse_orig_tx_contract_invoke(tx) -> Optional[Dict]:
    for op in tx.get("operations"):
        if op[0] == TxType.TxTypeContractInvoke.value:
            return op[1]
    return None


def block_consuming() -> None:
    while Application.consuming_thread_running:
        latest_height = http_get_block_height(Application.setting.API_URL)
        next_consuming_height = int(query_next_consume_height().value)

        if next_consuming_height > latest_height - 3:
            time.sleep(3)
            continue

        with Application.database_proxy.transaction():
            block = http_get_block(Application.setting.API_URL, next_consuming_height)
            tx_hash_list = block.get("transaction_ids")
            block_datetime = utc_time_str_to_datetime(block.get("timestamp"))

            for tx_hash in tx_hash_list:
                tx = http_get_transaction_by_hash(Application.setting.API_URL, tx_hash)

                tx_type = parse_tx_type(tx)
                if tx_type == TxType.TxTypeOther:
                    # Ignore irrelevant transactions
                    continue

                tx_receipt = http_get_contract_invoke_object(Application.setting.API_URL, next_consuming_height)
                if tx_type == TxType.TxTypeContractRegister:
                    exec_succeed, invoker, contract_registed = parse_tx_contract_register_result(tx_receipt)
                    if not exec_succeed:
                        # Ignore unsuccessful registration contracts
                        continue

                    printable_bytecode = http_get_contract_printable_bytecode(Application.setting.API_URL,
                                                                              contract_registed)
                    if Application.otc_ex_bytecode_hex != printable_bytecode:
                        # Ignore unrelated contracts
                        continue

                    if query_market_state_by_creater(invoker) is not None:
                        # Ignored if invoker has already registered a contract before
                        continue

                    insert_market_state(contract_registed, invoker, next_consuming_height, block_datetime)

                elif tx_type == TxType.TxTypeContractInvoke:
                    exec_succeed, invoker, events = parse_tx_contract_invoke_result(tx_receipt)
                    if not exec_succeed:
                        # Ignore unsuccessful registration contracts
                        continue

                    op = parse_orig_tx_contract_invoke(tx)
                    if op is None:
                        continue

                    market_state = query_market_state_by_market_id(op.get("contract_id"))
                    if market_state is None:
                        # Ignore if it's a contract we don't care about
                        continue

                    state_orders = json.loads(market_state.state_orders)
                    if op.get("contract_api") == "cancelSellOrderPair":
                        p = op.get("contract_arg").split(",")
                        state_orders = [
                            state_order for state_order in state_orders
                            if not (
                                    state_order.get("sellAsset") == p[0]
                                    and state_order.get("buyAsset") == p[1]
                            )
                        ]
                    elif op.get("contract_api") == "cancelAllOrder":
                        state_orders = []
                    elif op.get("contract_api") == "close":
                        state_orders = []
                    elif op.get("contract_api") == "putOnSellOrder":
                        p = op.get("contract_arg").split(",")
                        same_price = False
                        for i in range(len(state_orders)):
                            if state_orders[i].get("sellAsset") == p[0] \
                                    and state_orders[i].get("buyAsset") == p[2] \
                                    and state_orders[i].get("sellAssetLeft") / state_orders[i].get("buyAssetLeft") == \
                                    int(p[1]) / int(p[3]):
                                same_price = True
                                state_orders[i]["sellAssetLeft"] = state_orders[i]["sellAssetLeft"] + int(p[1])
                                state_orders[i]["buyAssetLeft"] = state_orders[i]["buyAssetLeft"] + int(p[3])
                                break
                        if not same_price:
                            new_order = {
                                "marketId": op.get("contract_id"),
                                "orderCreateHeight": next_consuming_height,
                                "orderCreateTx": tx_hash,
                                "sellAsset": p[0],
                                "sellAssetLeft": int(p[1]),
                                "buyAsset": p[2],
                                "buyAssetLeft": int(p[3]),
                            }
                            state_orders.append(new_order)
                    elif op.get("contract_api") == "cancelSellOrder":
                        p = op.get("contract_arg").split(",")
                        state_orders = [
                            state_order for state_order in state_orders
                            if not (
                                    state_order.get("sellAsset") == p[0]
                                    and state_order.get("sellAssetLeft") == int(p[1])
                                    and state_order.get("buyAsset") == p[2]
                                    and state_order.get("buyAssetLeft") == int(p[3])
                            )
                        ]

                    market_state.state_orders = json.dumps(state_orders)
                    market_state.state_height = next_consuming_height
                    market_state.state_timestamp = block_datetime

                    TMarketState.update(market_state).execute()

                else:
                    pass

            next_consuming_height = next_consuming_height + 1
            update_next_consume_height(next_consuming_height)


def run_block_consuming_thread() -> None:
    Application.consuming_thread = threading.Thread(target=block_consuming, daemon=False)
    Application.consuming_thread_running = True
    Application.consuming_thread.start()
