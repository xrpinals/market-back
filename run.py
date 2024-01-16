#!/usr/bin/env python
# encoding: utf-8


import os

import uvicorn  # type: ignore
from dotenv import load_dotenv

from app import create_app

if __name__ == "__main__":
    load_dotenv()
    use_config = os.environ.get("USE_CONFIG")

    app = create_app(use_config)
    uvicorn.run(app, host="0.0.0.0", port=2901)
