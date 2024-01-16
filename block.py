#!/usr/bin/env python
# encoding: utf-8
import threading
from crud import *
from rpc import *
from config import Application


def block_consuming():
    while Application.consuming_thread_running:
        latest_height = http_get_block_height(Application.setting.API_URL)
        next_consuming_height = int(query_next_consume_height().value)
        print(latest_height, next_consuming_height)


def run_block_consuming_thread():
    Application.consuming_thread = threading.Thread(target=block_consuming, daemon=False)
    Application.consuming_thread_running = True
    Application.consuming_thread.start()
