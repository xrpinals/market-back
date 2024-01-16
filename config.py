#!/usr/bin/env python
# encoding: utf-8
import os
from threading import Thread
from typing import Union, Optional

from dotenv import load_dotenv
from peewee import DatabaseProxy  # type: ignore


class BaseConfig:
    pass


class DevelopmentConfig(BaseConfig):
    load_dotenv()
    DATABASE_USER: Optional[str] = os.environ.get("DEV_DB_USER")
    DATABASE_PASS: Optional[str] = os.environ.get("DEV_DB_PASSWORD")
    DATABASE_HOST: Optional[str] = os.environ.get("DEV_DB_HOST")
    DATABASE_PORT: int = int(os.environ.get("DEV_DB_PORT", 3306))
    DATABASE_NAME: Optional[str] = os.environ.get("DEV_DB_NAME")
    DATABASE_CHARSET: Optional[str] = os.environ.get("DEV_DB_CHARSET")
    API_URL: Optional[str] = os.environ.get("DEV_API_URL")


class ProductionConfig(BaseConfig):
    load_dotenv()
    DATABASE_USER: Optional[str] = os.environ.get("PROD_DB_USER")
    DATABASE_PASS: Optional[str] = os.environ.get("PROD_DB_PASSWORD")
    DATABASE_HOST: Optional[str] = os.environ.get("PROD_DB_HOST")
    DATABASE_PORT: int = int(os.environ.get("PROD_DB_PORT", 3306))
    DATABASE_NAME: Optional[str] = os.environ.get("PROD_DB_NAME")
    DATABASE_CHARSET: Optional[str] = os.environ.get("PROD_DB_CHARSET")
    API_URL: Optional[str] = os.environ.get("PROD_API_URL")


configs = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


class Application(object):
    setting: Union[DevelopmentConfig, ProductionConfig, None] = None
    database_proxy: Optional[DatabaseProxy] = None
    otc_ex_bytecode_hex: str = ""
    consuming_thread: Optional[Thread] = None
    consuming_thread_running: bool = False
