#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConnectorSpecification, Status, Type
from jsonschema import Draft7Validator
from source_chargebee import SourceChargebee


@responses.activate
def test_discover_v1(test_config_v1):
    source = SourceChargebee()
    logger_mock = MagicMock()
    catalog = source.discover(logger_mock, test_config_v1)
    catalog = AirbyteMessage(type=Type.CATALOG, catalog=catalog).dict(exclude_unset=True)
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]
    for schema in schemas:
        Draft7Validator.check_schema(schema)


@responses.activate
def test_discover_v2(test_config_v2):
    source = SourceChargebee()
    logger_mock = MagicMock()
    catalog = source.discover(logger_mock, test_config_v2)
    catalog = AirbyteMessage(type=Type.CATALOG, catalog=catalog).dict(exclude_unset=True)
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]
    for schema in schemas:
        Draft7Validator.check_schema(schema)


def test_spec():
    source = SourceChargebee()
    logger_mock = MagicMock()
    spec = source.spec(logger_mock)
    assert isinstance(spec, ConnectorSpecification)


@responses.activate
def test_check_v1(test_config_v1):
    responses.add(
        responses.GET,
        "https://airbyte-test.chargebee.com/api/v2/subscriptions",
        json={"list": [{"subscription": {"id": "cbdemo_cancelled_sub"}, "customer": {}, "card": {}}]},
    )
    source = SourceChargebee()
    logger_mock = MagicMock()
    assert source.check(logger_mock, test_config_v1) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert len(responses.calls) == 1


@responses.activate
def test_check_v2(test_config_v2):
    responses.add(
        responses.GET,
        "https://airbyte-test.chargebee.com/api/v2/subscriptions",
        json={"list": [{"subscription": {"id": "cbdemo_cancelled_sub"}, "customer": {}, "card": {}}]},
    )
    source = SourceChargebee()
    logger_mock = MagicMock()
    assert source.check(logger_mock, test_config_v2) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert len(responses.calls) == 1


@responses.activate
def test_check_error_v1(test_config_v1):
    source = SourceChargebee()
    logger_mock = MagicMock()
    assert source.check(logger_mock, test_config_v1).status == Status.FAILED
    assert len(responses.calls) == 1


@responses.activate
def test_check_error_v2(test_config_v2):
    source = SourceChargebee()
    logger_mock = MagicMock()
    assert source.check(logger_mock, test_config_v2).status == Status.FAILED
    assert len(responses.calls) == 1


@responses.activate
def test_source_streams_v1(test_config_v1):
    source = SourceChargebee()
    streams = source.streams(test_config_v1)
    assert len(streams) == 10
    actual_stream_names = {stream.name for stream in streams}
    expected_stream_names = {
        "coupon",
        "credit_note",
        "customer",
        "event",
        "invoice",
        "order",
        "subscription",
        "addon",
        "plan",
        "transaction",
    }
    assert expected_stream_names == actual_stream_names


@responses.activate
def test_source_streams_v2(test_config_v2):
    source = SourceChargebee()
    streams = source.streams(test_config_v2)
    assert len(streams) == 11
    actual_stream_names = {stream.name for stream in streams}
    expected_stream_names = {
        "coupon",
        "credit_note",
        "customer",
        "event",
        "invoice",
        "order",
        "subscription",
        "item",
        "item_price",
        "attached_item",
        "transaction",
    }
    assert expected_stream_names == actual_stream_names
