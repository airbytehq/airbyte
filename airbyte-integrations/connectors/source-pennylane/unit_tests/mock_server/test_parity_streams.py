# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import freezegun
import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import discover
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.helpers import read_stream
from mock_server.request_builder import list_request, list_response


TOP_LEVEL_STREAMS = (
    "bank_establishments",
    "customer_invoice_templates",
    "sepa_mandates",
    "gocardless_mandates",
)


@pytest.mark.parametrize("stream_name", TOP_LEVEL_STREAMS)
def test_cursor_pagination(stream_name: str) -> None:
    with HttpMocker() as http_mocker:
        first = list_request(stream_name)
        second = list_request(stream_name, "next-page")
        http_mocker.get(first, list_response([{"id": 1}], "next-page"))
        http_mocker.get(second, list_response([{"id": 2}]))

        output = read_stream(stream_name, SyncMode.full_refresh, ConfigBuilder().build())

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [1, 2]
        http_mocker.assert_number_of_calls(first, 1)
        http_mocker.assert_number_of_calls(second, 1)


@pytest.mark.parametrize("stream_name", TOP_LEVEL_STREAMS)
def test_empty_stream(stream_name: str) -> None:
    with HttpMocker() as http_mocker:
        request = list_request(stream_name)
        http_mocker.get(request, list_response([]))

        output = read_stream(stream_name, SyncMode.full_refresh, ConfigBuilder().build())

        assert output.errors == []
        assert output.records == []
        http_mocker.assert_number_of_calls(request, 1)


@freezegun.freeze_time("2024-06-01T00:00:00Z")
@pytest.mark.parametrize("missing_customer", [False, True], ids=["two-customers", "missing-customer"])
def test_customer_contacts(missing_customer: bool) -> None:
    with HttpMocker() as http_mocker:
        customers = list_request("customers")
        first = list_request("customers/10/contacts")
        second_page = list_request("customers/10/contacts", "contacts-next")
        second = list_request("customers/20/contacts")
        http_mocker.get(
            customers,
            list_response([{"id": customer_id, "updated_at": "2024-02-01T10:00:00.000Z"} for customer_id in (10, 20)]),
        )
        http_mocker.get(first, list_response([{"id": 1}], "contacts-next"))
        http_mocker.get(second_page, list_response([{"id": 2}]))
        http_mocker.get(second, HttpResponse(body="{}", status_code=404) if missing_customer else list_response([{"id": 1}]))

        output = read_stream("customer_contacts", SyncMode.full_refresh, ConfigBuilder().build())

        assert output.errors == []
        records = [message.record.data for message in output.records]
        expected = [(10, 1), (10, 2)] if missing_customer else [(10, 1), (10, 2), (20, 1)]
        assert sorted((record["customer_id"], record["id"]) for record in records) == expected
        assert all(type(record["customer_id"]) is int for record in records)
        for request in (customers, first, second_page, second):
            http_mocker.assert_number_of_calls(request, 1)


@freezegun.freeze_time("2024-06-01T00:00:00Z")
def test_customer_contacts_empty_parent() -> None:
    with HttpMocker() as http_mocker:
        request = list_request("customers")
        http_mocker.get(request, list_response([]))

        output = read_stream("customer_contacts", SyncMode.full_refresh, ConfigBuilder().build())

        assert output.errors == []
        assert output.records == []
        http_mocker.assert_number_of_calls(request, 1)


def test_discover_parity_streams() -> None:
    config = ConfigBuilder().build()
    output = discover(get_source(config=config), config=config)
    streams = {stream.name: stream for stream in output.catalog.catalog.streams}

    assert set(TOP_LEVEL_STREAMS + ("customer_contacts",)) <= streams.keys()
    for name in TOP_LEVEL_STREAMS:
        assert streams[name].source_defined_primary_key == [["id"]]
        assert streams[name].supported_sync_modes == [SyncMode.full_refresh]
    assert streams["customer_contacts"].source_defined_primary_key == [["customer_id"], ["id"]]
    assert streams["customer_contacts"].supported_sync_modes == [SyncMode.full_refresh]
