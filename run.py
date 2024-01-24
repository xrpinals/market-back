#!/usr/bin/env python
# encoding: utf-8


import os
import signal
import sys

import uvicorn  # type: ignore
from dotenv import load_dotenv
from block import run_block_consuming_thread
from statistics import run_market_statistics_thread
from config import Application
from app import create_app


def handle_sig(sig: int, _) -> None:
    print("Caught Signal: %d, Please wait a few seconds for Threads Stopping..." % sig)
    Application.consuming_thread_running = False
    Application.consuming_thread.join()
    print("Consuming Thread Stopped!")
    Application.statistics_thread_running = False
    Application.statistics_thread.join()
    print("Statistics Thread Stopped!")
    sys.exit(0)


if __name__ == "__main__":
    load_dotenv()
    use_config = os.environ.get("USE_CONFIG", "development")

    app = create_app(use_config)
    run_block_consuming_thread()
    run_market_statistics_thread()
    uvicorn.run(app, host="0.0.0.0", port=2901)

    # out of uvicorn event loop
    # pretending we catch the interrupt signal and then stop consuming thread
    handle_sig(signal.SIGINT, None)
