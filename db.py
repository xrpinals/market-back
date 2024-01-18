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


class TMarket(BaseModel):
    base_symbol = CharField(null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    market_create_datetime = DateTimeField()
    market_create_height = IntegerField()
    market_id = CharField()
    market_name = CharField(null=True)
    market_status = IntegerField()
    owner = CharField()
    quote_symbol = CharField(null=True)
    updated_at = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)

    class Meta:
        table_name = 't_market'


class TOrder(BaseModel):
    buyer = CharField(null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)
    expect_buy_amount = DecimalField()
    expect_buy_symbol = CharField()
    fee = DecimalField(null=True)
    market_id = CharField()
    order_idx = IntegerField()
    order_placed_datetime = DateTimeField()
    order_placed_height = IntegerField()
    order_placed_tx = CharField()
    order_status = IntegerField()
    sell_amount = DecimalField()
    sell_symbol = CharField()
    seller = CharField()
    trade_datetime = DateTimeField(null=True)
    trade_height = IntegerField(null=True)
    trade_tx = CharField(null=True)
    updated_at = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")], null=True)

    class Meta:
        table_name = 't_order'
