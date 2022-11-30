#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import os

from pytest import fixture


def load_file(fn):
    return open(os.path.join("unit_tests", "responses", fn)).read()


@fixture
def test_config_v1():
    return {"site": "airbyte-test", "site_api_key": "site_api_key", "start_date": "2021-05-22T06:57:44Z", "product_catalog": "1.0"}


@fixture
def test_config_v2():
    return {"site": "airbyte-test", "site_api_key": "site_api_key", "start_date": "2021-05-22T06:57:44Z", "product_catalog": "2.0"}


@fixture
def addons_response():
    return json.loads(load_file("addons.json"))


@fixture
def plans_response():
    return json.loads(load_file("plans.json"))


@fixture
def coupons_response():
    return json.loads(load_file("coupons.json"))


@fixture
def customers_response():
    return json.loads(load_file("customers.json"))


@fixture
def invoices_response():
    return json.loads(load_file("invoices.json"))


@fixture
def orders_response():
    return json.loads(load_file("orders.json"))


@fixture
def events_response():
    return json.loads(load_file("events.json"))


@fixture
def subscriptions_response():
    return json.loads(load_file("subscriptions.json"))


@fixture
def items_response():
    return json.loads(load_file("items.json"))


@fixture
def item_prices_response():
    return json.loads(load_file("item_prices.json"))


@fixture
def attached_items_response():
    return json.loads(load_file("attached_items.json"))
