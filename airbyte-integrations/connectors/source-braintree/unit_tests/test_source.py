#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import jsonschema
import responses
from airbyte_cdk.models import AirbyteMessage, Type
from source_braintree.source import SourceBraintree


def get_stream_by_name(streams: list, stream_name: str):
    for stream in streams:
        if stream.name == stream_name:
            return stream


def test_source_streams(test_config):
    s = SourceBraintree()
    streams = s.streams(test_config)
    assert len(streams) == 7
    assert {stream.name for stream in streams} == {
        "customer_stream",
        "discount_stream",
        "dispute_stream",
        "transaction_stream",
        "merchant_account_stream",
        "plan_stream",
        "subscription_stream",
    }
    customers = get_stream_by_name(streams, "customer_stream")
    assert customers.supports_incremental
    discount_stream = get_stream_by_name(streams, "discount_stream")
    assert not discount_stream.supports_incremental


def test_discover(test_config):
    source = SourceBraintree()
    catalog = source.discover(None, test_config)
    catalog = AirbyteMessage(type=Type.CATALOG, catalog=catalog).dict(exclude_unset=True)
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]
    for schema in schemas:
        jsonschema.Draft7Validator.check_schema(schema)


def test_spec(test_config):
    s = SourceBraintree()
    schema = s.spec(None).connectionSpecification
    jsonschema.Draft4Validator.check_schema(schema)
    jsonschema.validate(instance=test_config, schema=schema)


@responses.activate
def test_check(test_config):
    s = SourceBraintree()
    responses.add(
        responses.POST,
        "https://api.sandbox.braintreegateway.com:443/merchants/mech_id/customers/advanced_search_ids",
        body=open("unit_tests/data/customers_ids.txt").read(),
    )
    assert s.check_connection(None, test_config) == (True, "")
