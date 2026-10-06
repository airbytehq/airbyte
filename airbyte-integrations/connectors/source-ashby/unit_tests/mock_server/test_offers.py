# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `offers` stream on `source-ashby`.

`POST /offer.list` paginates with `cursor` and `limit` in the JSON body, and
the tests assert the exact request bodies the connector sends for each page.
"""

import json
import logging
from typing import Any, Dict, List
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import AshbyRequestBuilder


_STREAM_NAME = "offers"


def _offer_version(version_id: str) -> Dict[str, Any]:
    return {
        "id": version_id,
        "startDate": "2024-07-01",
        "salary": {"currencyCode": "USD", "value": 100000},
        "createdAt": "2024-06-15T12:00:00Z",
        "openingId": "opening-1",
        "customFields": [],
        "fileHandles": [],
        "author": {
            "id": "user-1",
            "firstName": "Ana",
            "lastName": "Example",
            "email": "ana@example.com",
        },
        "approvalStatus": "Approved",
    }


def _offer_record(record_id: str, **overrides) -> Dict[str, Any]:
    record = {
        "id": record_id,
        "applicationId": "app-1",
        "acceptanceStatus": "Pending",
        "offerStatus": "Open",
        "decidedAt": "2024-06-20T12:00:00Z",
        "formDefinition": {},
        "latestVersion": _offer_version("ver-1"),
        "versions": [_offer_version("ver-1")],
    }
    record.update(overrides)
    return record


def _page(records: List[Dict[str, Any]], next_cursor: str = None) -> HttpResponse:
    body = {
        "success": True,
        "results": records,
        "moreDataAvailable": next_cursor is not None,
    }
    if next_cursor is not None:
        body["nextCursor"] = next_cursor
    return HttpResponse(body=json.dumps(body), status_code=200)


def _first_page_request() -> HttpRequest:
    return AshbyRequestBuilder.offers_endpoint().with_api_key("test-api-key").with_limit(100).build()


def _read() -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=config), config=config, catalog=catalog, state=StateBuilder().build())


class TestOffers(TestCase):
    @HttpMocker()
    def test_reads_all_pages_with_exact_request_bodies(self, http_mocker: HttpMocker):
        """Each page is a POST whose JSON body is exactly `limit` and the returned cursor."""
        first_page = _first_page_request()
        second_page = AshbyRequestBuilder.offers_endpoint().with_api_key("test-api-key").with_limit(100).with_cursor("cursor-2").build()
        http_mocker.post(first_page, _page([_offer_record("offer-1"), _offer_record("offer-2")], next_cursor="cursor-2"))
        http_mocker.post(second_page, _page([_offer_record("offer-3")]))

        output = _read()

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == ["offer-1", "offer-2", "offer-3"]
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)

    @HttpMocker()
    def test_record_keeps_nested_objects_verbatim(self, http_mocker: HttpMocker):
        """`latestVersion` and `versions` pass through untouched."""
        http_mocker.post(_first_page_request(), _page([_offer_record("offer-1")]))

        output = _read()

        assert output.errors == []
        record = output.records[0].record.data
        assert record["latestVersion"] == _offer_version("ver-1")
        assert record["versions"] == [_offer_version("ver-1")]

    def test_discover_declares_offers_stream(self):
        """Discovery declares the stream with `id` primary key and full_refresh only."""
        config = ConfigBuilder().build()
        catalog = get_source(config=config).discover(logging.getLogger("airbyte"), config)
        streams_by_name = {stream.name: stream for stream in catalog.streams}
        stream = streams_by_name[_STREAM_NAME]

        assert stream.source_defined_primary_key == [["id"]]
        assert stream.supported_sync_modes == [SyncMode.full_refresh]
