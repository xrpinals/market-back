#!/usr/bin/env python
# encoding: utf-8
import threading
import time
from typing import Optional

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

                    TMarketState.insert(market_id=contract_registed, creater=invoker,
                                        create_height=next_consuming_height,
                                        state_orders="[]", state_height=next_consuming_height,
                                        state_timestamp=block_datetime, created_at=datetime.now(),
                                        updated_at=datetime.now()).execute()

                elif tx_type == TxType.TxTypeContractInvoke:
                    pass
                else:
                    pass

            next_consuming_height = next_consuming_height + 1
            update_next_consume_height(next_consuming_height)


def run_block_consuming_thread() -> None:
    Application.consuming_thread = threading.Thread(target=block_consuming, daemon=False)
    Application.consuming_thread_running = True
    Application.consuming_thread.start()
