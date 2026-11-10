# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from pathlib import Path

import requests
from source_braintree.source import DiscountExtractor, SourceBraintree

from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, Type


def test_spec():
    spec = SourceBraintree().spec(logging.getLogger("airbyte"))
    expected_spec = json.loads(Path("integration_tests/spec.json").read_text())

    assert spec.connectionSpecification == expected_spec["connectionSpecification"]


def test_streams():
    config = json.loads(Path("integration_tests/sample_config.json").read_text())
    streams = SourceBraintree().streams(config)

    assert {stream.name for stream in streams} == {
        "customer_stream",
        "discount_stream",
        "dispute_stream",
        "merchant_account_stream",
        "plan_stream",
        "subscription_stream",
        "transaction_stream",
    }


def test_discount_extractor_record_parity():
    response = requests.Response()
    response._content = b"""<discounts type="array"><item><amount>2.00</amount><description>This is test discount</description><id>dissscount</id><kind>discount</kind><name>test discount</name><never-expires type="boolean">true</never-expires><number-of-billing-cycles nil="true"/></item></discounts>"""
    response.encoding = "utf-8"
    records = DiscountExtractor().extract_records(response)
    expected_record = next(
        json.loads(line)
        for line in Path("integration_tests/expected_records.jsonl").read_text().splitlines()
        if json.loads(line)["stream"] == "discount_stream"
    )

    messages = [
        AirbyteEntrypoint.airbyte_message_to_string(
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    stream="discount_stream",
                    data=record,
                    emitted_at=expected_record["emitted_at"],
                ),
            )
        )
        for record in records
    ]

    assert [json.loads(message)["record"]["data"] for message in messages] == [expected_record["data"]]
