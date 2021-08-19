#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
from copy import deepcopy

import pendulum
import responses
from airbyte_cdk.models import SyncMode
from freezegun import freeze_time
from source_braintree.spec import BraintreeConfig
from source_braintree.streams import (
    CustomerStream,
    DiscountStream,
    DisputeStream,
    MerchantAccountStream,
    PlanStream,
    SubscriptionStream,
    TransactionStream,
)


def load_file(fn):
    return open(os.path.join("unit_tests", "data", fn)).read()


def read_all_records(stream):
    stream_slice = {stream.cursor_field or "start_date": pendulum.utcnow()}
    return [r for r in stream.read_records(None, None, stream_slice)]


@responses.activate
def test_customers_stream(test_config):
    responses.add(
        responses.POST,
        "https://api.sandbox.braintreegateway.com:443/merchants/mech_id/customers/advanced_search_ids",
        body=load_file("customers_ids.txt"),
    )
    responses.add(
        responses.POST,
        "https://api.sandbox.braintreegateway.com:443/merchants/mech_id/customers/advanced_search",
        body=load_file("customers_obj_response.txt"),
    )
    config = BraintreeConfig(**test_config)
    stream = CustomerStream(config)
    records = read_all_records(stream)
    assert len(records) == 1


@responses.activate
def test_transaction_stream(test_config):
    responses.add(
        responses.POST,
        "https://api.sandbox.braintreegateway.com:443/merchants/mech_id/transactions/advanced_search_ids",
        body=load_file("transaction_ids.txt"),
    )
    responses.add(
        responses.POST,
        "https://api.sandbox.braintreegateway.com:443/merchants/mech_id/transactions/advanced_search",
        body=load_file("transaction__objs.txt"),
    )
    config = BraintreeConfig(**test_config)
    stream = TransactionStream(config)
    records = read_all_records(stream)
    assert len(records) == 2


@responses.activate
def test_discount(test_config):
    responses.add(
        responses.GET,
        "https://api.sandbox.braintreegateway.com:443/merchants/mech_id/discounts/",
        body=load_file("discounts.txt"),
    )
    config = BraintreeConfig(**test_config)
    stream = DiscountStream(config)
    records = read_all_records(stream)
    assert len(records) == 1


@responses.activate
def test_merch_account(test_config):
    responses.add(
        responses.GET,
        "https://api.sandbox.braintreegateway.com:443/merchants/mech_id/merchant_accounts/",
        body=load_file("merch_account.txt"),
    )
    config = BraintreeConfig(**test_config)
    stream = MerchantAccountStream(config)
    records = read_all_records(stream)
    assert len(records) == 1


@responses.activate
def test_plan(test_config):
    responses.add(
        responses.GET,
        "https://api.sandbox.braintreegateway.com:443/merchants/mech_id/plans/",
        body=load_file("plans.txt"),
    )
    config = BraintreeConfig(**test_config)
    stream = PlanStream(config)
    records = read_all_records(stream)
    assert len(records) == 1


@responses.activate
def test_dispute(test_config):
    responses.add(
        responses.POST,
        "https://api.sandbox.braintreegateway.com:443/merchants/mech_id/disputes/advanced_search",
        body=load_file("disputes.txt"),
    )
    config = BraintreeConfig(**test_config)
    stream = DisputeStream(config)
    records = read_all_records(stream)
    assert len(records) == 1


@responses.activate
def test_subscription(test_config):
    responses.add(
        responses.POST,
        "https://api.sandbox.braintreegateway.com:443/merchants/mech_id/subscriptions/advanced_search_ids",
        body=load_file("subscriptions.txt"),
    )
    config = BraintreeConfig(**test_config)
    stream = SubscriptionStream(config)
    records = read_all_records(stream)
    assert len(records) == 0


@freeze_time("2020-10-10")
def test_stream_slices(test_config):
    config = BraintreeConfig(**test_config)
    stream = TransactionStream(config)

    assert stream.stream_slices(SyncMode.incremental, None, {}) == [{stream.cursor_field: config.start_date}]
    assert stream.stream_slices(SyncMode.incremental, None, {stream.cursor_field: "2010"}) == [
        {stream.cursor_field: pendulum.datetime(2010, 1, 1)}
    ]
    assert stream.stream_slices(SyncMode.full_refresh, None, {stream.cursor_field: "2010"}) == [{stream.cursor_field: config.start_date}]

    test_config = deepcopy(test_config)
    test_config.pop("start_date")
    config = BraintreeConfig(**test_config)
    stream = TransactionStream(config)
    assert stream.stream_slices(SyncMode.incremental, None, {}) == [{stream.cursor_field: pendulum.datetime(2020, 10, 10)}]
    assert stream.stream_slices(SyncMode.full_refresh, None, {stream.cursor_field: "2010"}) == [
        {stream.cursor_field: pendulum.datetime(2020, 10, 10)}
    ]


def test_updated_state(test_config):
    config = BraintreeConfig(**test_config)
    stream = TransactionStream(config)

    assert stream.get_updated_state({stream.cursor_field: "2021-08-10 14:32:39"}, {stream.cursor_field: pendulum.parse("2000")}) == {
        stream.cursor_field: "2021-08-10 14:32:39"
    }
    assert stream.get_updated_state({stream.cursor_field: "2021-08-10 14:32:39"}, {stream.cursor_field: pendulum.parse("2100")}) == {
        stream.cursor_field: "2100-01-01 00:00:00"
    }
    assert stream.get_updated_state({}, {stream.cursor_field: pendulum.parse("2100")}) == {stream.cursor_field: "2100-01-01 00:00:00"}
