from peewee import *

database_proxy = DatabaseProxy()


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database_proxy


class TGlobal(BaseModel):
    value = CharField()
    variate = CharField()

    class Meta:
        table_name = 't_global'


class TMarketHistory(BaseModel):
    buyer_address = CharField()
    created_at = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    market_id = CharField()
    sell_amount = DecimalField()
    sell_asset = CharField()
    sell_price = DecimalField()
    seller_address = CharField()
    tx_hash = CharField()
    tx_height = IntegerField()
    tx_timestamp = DateTimeField()
    updated_at = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])

    class Meta:
        table_name = 't_market_history'


class TMarketState(BaseModel):
    create_height = IntegerField()
    created_at = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    creater = CharField()
    market_id = CharField()
    state_height = IntegerField()
    state_orders = TextField()
    state_timestamp = DateTimeField()
    updated_at = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])

    class Meta:
        table_name = 't_market_state'
