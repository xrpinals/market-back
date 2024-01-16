#!/usr/bin/env python
# encoding: utf-8
from abc import ABC

from fastapi import FastAPI
from peewee import SENTINEL, MySQLDatabase, InterfaceError  # type: ignore
from playhouse.shortcuts import ReconnectMixin  # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from db import database_proxy  # type: ignore

from config import configs, Application, DevelopmentConfig


class ReconnectMixinNew(ReconnectMixin):
    def execute_sql(self, sql, params=None, commit=SENTINEL):
        try:
            return super(ReconnectMixin, self).execute_sql(sql, params, commit)
        except Exception as exc:
            exc_class = type(exc)
            if exc_class not in self._reconnect_errors and exc_class is not InterfaceError:
                raise exc

            if exc_class in self._reconnect_errors:
                exc_repr = str(exc).lower()
                for err_fragment in self._reconnect_errors[exc_class]:
                    if err_fragment in exc_repr:
                        break
                else:
                    raise exc

            if not self.is_closed():
                self.close()
                self.connect()

            return super(ReconnectMixin, self).execute_sql(sql, params, commit)


class ReconnectMySQLDatabase(ReconnectMixinNew, MySQLDatabase, ABC):
    pass


def create_app(config_name: str) -> FastAPI:
    setting = configs.get(config_name, DevelopmentConfig)
    Application.setting = setting

    f = open("contract/otc-ex.bytecode.hex", "r")
    Application.otc_ex_bytecode_hex = f.read(1024 * 1024) \
        .lstrip().rstrip() \
        .replace("\n", "") \
        .replace("\r", "")

    db = ReconnectMySQLDatabase(
        setting.DATABASE_NAME, autocommit=True, autorollback=True,
        **{'host': setting.DATABASE_HOST, 'port': setting.DATABASE_PORT,
           'user': setting.DATABASE_USER,
           'password': setting.DATABASE_PASS,
           'use_unicode': True,
           'charset': setting.DATABASE_CHARSET})
    database_proxy.initialize(db)
    Application.database_proxy = database_proxy

    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
