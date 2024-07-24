import json
import datetime
from peewee import SqliteDatabase, Model, IntegerField, DateField, CharField, ForeignKeyField


database = SqliteDatabase(json.load(open('config.json'))['DATABASE'])


class Weight(Model):
    weight = IntegerField()
    date = DateField()

    class Meta:
        database = database


class Restaurant(Model):
    name = CharField()
    rating = IntegerField(null=True)
    last_order = DateField(default=datetime.datetime.now().date())

    class Meta:
        database = database


class Order(Model):
    restaurant_id = ForeignKeyField(Restaurant, backref='restaurant')
    order_date = DateField(default=datetime.datetime.now().date())
    notes = CharField(null=True)

    class Meta:
        database = database


class OrderItem(Model):
    restaurant_id = ForeignKeyField(Restaurant, backref='restaurant')
    name = CharField()
    min_price = IntegerField()
    max_price = IntegerField()
    last_price = IntegerField()
    rating = IntegerField(null=True)
    notes = CharField(null=True)
    last_order = DateField(default=datetime.datetime.now().date())

    class Meta:
        database = database


class OrderMap(Model):
    item_id = ForeignKeyField(OrderItem, backref='item')
    order_id = ForeignKeyField(Order, backref='order')

    class Meta:
        primary_key = False
        database = database


class Nessus(Model):
    name = CharField()
    action = CharField()      # enum: ALERT, IGNORE
    # note that cvsss maps to PLUGIN severity, not CVE score (4 = critical, 3 = high, 2 = medium, 1 = low)
    identifier = CharField()  # enum: <type:id>, e.g. "cve:cve-2024-11111", "cvss:4", or "pluginid:201969"
    rationale = CharField()

    class Meta:
        database = database


def create_nessus_tables():
    database.create_tables([Nessus])


def drop_nessus_tables():
    database.drop_tables([Nessus])


def create_tables():
    database.create_tables([Weight, Restaurant, Order, OrderItem, OrderMap])


def drop_tables():
    database.drop_tables([Restaurant, Order, OrderItem, OrderMap])
