# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Iterator

import pytest
from conftest import get_source
from jsonschema import Draft7Validator, FormatChecker

from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


TIMESTAMP = "2026-11-01T12:34:56Z"
CASES = [
    (
        "subscriptions",
        "subscriptions",
        {"coupon_redemptions": [{"id": "redemption-1", "created_at": TIMESTAMP}, {"id": "redemption-2", "created_at": TIMESTAMP}]},
        [],
    ),
    ("coupons", "coupons", {"redeem_by": TIMESTAMP}, [("redeem_by",)]),
    ("unique_coupons_parent", "coupons", {"coupon_type": "bulk", "created_at": TIMESTAMP}, [("created_at",), ("updated_at",)]),
    (
        "account_coupon_redemptions",
        "accounts/account-1/coupon_redemptions",
        {"coupon": {"redeem_by": TIMESTAMP}},
        [("coupon", "redeem_by")],
    ),
    (
        "accounts",
        "accounts",
        {"external_accounts": [{"id": "external-1", "created_at": TIMESTAMP, "updated_at": TIMESTAMP}]},
        [("external_accounts", 0, "created_at"), ("external_accounts", 0, "updated_at")],
    ),
]


@pytest.fixture
def http_mocker() -> Iterator[HttpMocker]:
    with HttpMocker() as mocker:
        yield mocker


def given_records(http_mocker: HttpMocker, endpoint: str, records: list[dict]) -> None:
    http_mocker.get(
        HttpRequest(
            url=f"https://v3.recurly.com/{endpoint}",
            query_params={
                "sort": "updated_at",
                "order": "asc",
                "limit": "200",
                "begin_time": "2026-11-01T00:00:00Z",
                "end_time": "2026-11-02T00:00:00Z",
            },
        ),
        HttpResponse(json.dumps({"data": records, "has_more": False})),
    )


@pytest.mark.parametrize("stream_name,endpoint,fields,date_paths", CASES, ids=[case[0] for case in CASES])
def test_emitted_records_conform_to_discovered_schema(
    stream_name: str, endpoint: str, fields: dict, date_paths: list[tuple], http_mocker: HttpMocker
) -> None:
    config = {"api_key": "test-api-key", "begin_time": "2026-11-01T00:00:00Z", "end_time": "2026-11-02T00:00:00Z"}
    stream = next(stream for stream in discover(get_source(config), config).catalog.catalog.streams if stream.name == stream_name)
    catalog = ConfiguredAirbyteCatalog(
        streams=[ConfiguredAirbyteStream(stream=stream, sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.append)]
    )
    record = {"id": "record-1", "updated_at": TIMESTAMP, **fields}
    if stream_name == "account_coupon_redemptions":
        given_records(http_mocker, "accounts", [{"id": "account-1", "updated_at": TIMESTAMP}])
    given_records(http_mocker, endpoint, [record])
    output = read(get_source(config), config, catalog)
    assert [message.record.data for message in output.records] == [record]
    validator = Draft7Validator(stream.json_schema, format_checker=FormatChecker())
    for message in output.records:
        validator.validate(message.record.data)
        for path in date_paths:
            schema = stream.json_schema
            value = message.record.data
            for key in path:
                schema = schema["items"] if isinstance(key, int) else schema["properties"][key]
                value = value[key]
            assert schema.get("format") == "date-time", path
            assert FormatChecker().conforms(value, "date-time"), path
