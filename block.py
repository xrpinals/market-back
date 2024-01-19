#!/usr/bin/env python
# encoding: utf-8

import threading
import time
from typing import Dict

from crud import *
from rpc import *
from utils import *
from config import Application
from enum import IntEnum


class OpType(IntEnum):
    OpTypeContractRegister = 76
    OpTypeContractInvoke = 79
    OpTypeTransferContract = 81


class TxType(IntEnum):
    TxTypeContractRegister = 1
    TxTypeContractInvoke = 2
    TxTypeTransferContract = 3
    TxTypeOther = -1


def parse_tx_type(tx) -> TxType:
    for op in tx.get("operations"):
        if op[0] == OpType.OpTypeContractRegister.value:
            return TxType.TxTypeContractRegister
        elif op[0] == OpType.OpTypeContractInvoke.value:
            return TxType.TxTypeContractInvoke
        elif op[0] == OpType.OpTypeTransferContract.value:
            return TxType.TxTypeTransferContract
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


def parse_tx_transfer_contract_result(tx_receipt) -> (bool, Optional[str], list):
    for obj in tx_receipt:
        if obj.get("exec_succeed"):
            return True, obj.get("invoker"), obj.get("events")
    return False, None, None


def parse_first_event_by_name(events: list, event_name: str) -> Optional[Dict]:
    for event in events:
        if event.get("event_name") == event_name:
            return event
    return None


def parse_orig_tx_contract_invoke(tx) -> Optional[Dict]:
    for op in tx.get("operations"):
        if op[0] == OpType.OpTypeContractInvoke.value:
            return op[1]
    return None


def parse_orig_tx_transfer_contract(tx) -> Optional[Dict]:
    for op in tx.get("operations"):
        if op[0] == OpType.OpTypeTransferContract.value:
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

                tx_receipt = http_get_contract_invoke_object(Application.setting.API_URL, tx_hash)
                if tx_type == TxType.TxTypeContractRegister:
                    exec_succeed, invoker, contract_registed = parse_tx_contract_register_result(tx_receipt)
                    if not exec_succeed:
                        # Ignore unsuccessful contract registering
                        continue

                    printable_bytecode = http_get_contract_printable_bytecode(Application.setting.API_URL,
                                                                              contract_registed)
                    if Application.otc_ex_bytecode_hex != printable_bytecode:
                        # Ignore unrelated contracts
                        continue

                    insert_new_market(market_id=contract_registed, owner=invoker, create_height=next_consuming_height,
                                      create_datetime=block_datetime)
                elif tx_type == TxType.TxTypeContractInvoke:
                    exec_succeed, invoker, events = parse_tx_contract_invoke_result(tx_receipt)
                    if not exec_succeed:
                        # Ignore unsuccessful contract invoking
                        continue

                    op = parse_orig_tx_contract_invoke(tx)
                    if op is None:
                        continue

                    contract_id = op.get("contract_id")
                    contract_api = op.get("contract_api")
                    contract_arg = op.get("contract_arg")

                    if contract_api == "open_market":
                        l = contract_arg.split(",")
                        if len(l) != 2:
                            continue

                        market_name = "-".join(l)
                        open_market(market_id=contract_id, market_name=market_name, base_symbol=l[0], quote_symbol=l[1])
                    elif contract_api == "close_market":
                        update_market_status(market_id=contract_id, old_market_status=MarketStatusOpen,
                                             new_market_status=MarketStatusClosed)
                    elif contract_api == "reopen_market":
                        update_market_status(market_id=contract_id, old_market_status=MarketStatusClosed,
                                             new_market_status=MarketStatusOpen)
                    elif contract_api == "cancel_order":
                        order_idx = int(contract_arg)
                        cancel_order(market_id=contract_id, order_idx=order_idx)

                elif tx_type == TxType.TxTypeTransferContract:
                    exec_succeed, invoker, events = parse_tx_transfer_contract_result(tx_receipt)
                    if not exec_succeed:
                        # Ignore unsuccessful contract transfering to
                        continue

                    op = parse_orig_tx_transfer_contract(tx)
                    if op is None:
                        continue

                    contract_id = op.get("contract_id")
                    caller_addr = op.get("caller_addr")
                    param = op.get("param")
                    l = param.split(",")
                    if len(l) not in (2, 3):
                        continue

                    if l[0] == "SELL":
                        event = parse_first_event_by_name(events, "PlaceOrder")
                        if event is not None:
                            ll = event.get("event_arg").split(",")
                            if len(ll) != 6:
                                continue

                            insert_new_order(market_id=contract_id, order_idx=int(ll[1]), seller=caller_addr,
                                             sell_symbol=ll[2], sell_amount=Decimal(ll[3]),
                                             expect_buy_symbol=ll[4],
                                             expect_buy_amount=Decimal(ll[5]), order_placed_tx=tx_hash,
                                             order_placed_height=next_consuming_height,
                                             order_placed_datetime=block_datetime)
                    elif l[0] == "BUY":
                        fee = Decimal(0)
                        event = parse_first_event_by_name(events, "ExchangeFee")
                        if event is not None:
                            ll = event.get("event_arg").split(",")
                            if len(ll) != 3:
                                continue
                            fee = Decimal(ll[2])

                        exchange_order(market_id=contract_id, order_idx=int(l[1]), trade_tx=tx_hash, buyer=caller_addr,
                                       fee=fee, trade_height=next_consuming_height,
                                       trade_datetime=block_datetime)
                    else:
                        pass
                else:
                    pass

            next_consuming_height = next_consuming_height + 1
            update_next_consume_height(next_consuming_height)


def run_block_consuming_thread() -> None:
    Application.consuming_thread = threading.Thread(target=block_consuming, daemon=False)
    Application.consuming_thread_running = True
    Application.consuming_thread.start()
