# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the IGNORE-on-400 error handler shared by the pretix streams."""

import json
from typing import Any, Dict, List
from unittest import TestCase
from unittest.mock import patch

import pytest
import yaml
from unit_tests.conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_BASE_URL = "https://pretix.eu/api/v1"
_CONFIG = {"api_token": "test-token"}
_PAGE_PARAMS = {"page": "1", "page_size": "50"}
_ORGANIZERS_REQUEST = HttpRequest(url=f"{_BASE_URL}/organizers", query_params=_PAGE_PARAMS)
_EXPECTED_ERROR_HANDLER = {
    "type": "DefaultErrorHandler",
    "response_filters": [
        {
            "type": "HttpResponseFilter",
            "action": "IGNORE",
            "http_codes": [400],
        }
    ],
}
_STREAMS_WITH_ERROR_HANDLER = [
    "orgainzers",
    "events",
    "tax_rules",
    "items",
    "orders",
    "vouchers",
    "discounts",
    "checkin_lists",
    "waiting_list_entries",
    "customers",
    "sales_channels",
    "membership_types",
    "memberships",
    "giftcards",
    "reusable_media",
    "teams",
    "devices",
    "webhooks",
    "seating_plans",
    "auto_checkin_rules",
]


def _events_request(organizer: str) -> HttpRequest:
    return HttpRequest(url=f"{_BASE_URL}/organizers/{organizer}/events", query_params=_PAGE_PARAMS)


def _results_response(records: List[Dict[str, Any]], status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps({"count": len(records), "next": None, "results": records}), status_code=status_code)


def _read(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog, expecting_exception=expecting_exception)


def _load_streams() -> Dict[str, Any]:
    return yaml.safe_load(_YAML_FILE_PATH.read_text())["definitions"]["streams"]


@patch("time.sleep", lambda _: None)
class TestPretixErrorHandler(TestCase):
    @HttpMocker()
    def test_organizers_records_are_emitted(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_ORGANIZERS_REQUEST, _results_response([{"slug": "org-a"}, {"slug": "org-b"}]))

        output = _read("orgainzers")

        assert [record.record.data["slug"] for record in output.records] == ["org-a", "org-b"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(_ORGANIZERS_REQUEST, 1)

    @HttpMocker()
    def test_400_is_ignored_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_ORGANIZERS_REQUEST, HttpResponse(body=json.dumps({"detail": "Bad request"}), status_code=400))

        output = _read("orgainzers")

        assert output.records == []
        assert output.errors == []
        http_mocker.assert_number_of_calls(_ORGANIZERS_REQUEST, 1)

    @HttpMocker()
    def test_400_on_one_partition_does_not_stop_other_partitions(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_ORGANIZERS_REQUEST, _results_response([{"slug": "org-a"}, {"slug": "org-b"}]))
        org_a_events_request = _events_request("org-a")
        http_mocker.get(org_a_events_request, HttpResponse(body=json.dumps({"detail": "Bad request"}), status_code=400))
        http_mocker.get(_events_request("org-b"), _results_response([{"slug": "event-1"}]))

        output = _read("events")

        assert [record.record.data["slug"] for record in output.records] == ["event-1"]
        assert output.errors == []
        http_mocker.assert_number_of_calls(org_a_events_request, 1)

    @HttpMocker()
    def test_401_fails_without_retry(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_ORGANIZERS_REQUEST, HttpResponse(body="", status_code=401))

        output = _read("orgainzers", expecting_exception=True)

        assert output.records == []
        assert output.errors
        http_mocker.assert_number_of_calls(_ORGANIZERS_REQUEST, 1)


def _error_handler_types(node: Any) -> List[str]:
    if isinstance(node, dict):
        found = [node["error_handler"]["type"]] if isinstance(node.get("error_handler"), dict) else []
        return found + [t for value in node.values() for t in _error_handler_types(value)]
    if isinstance(node, list):
        return [t for item in node for t in _error_handler_types(item)]
    return []


def test_every_error_handler_is_a_default_error_handler() -> None:
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())

    assert set(_error_handler_types(manifest)) == {"DefaultErrorHandler"}


@pytest.mark.parametrize("stream_name", _STREAMS_WITH_ERROR_HANDLER)
def test_stream_uses_default_error_handler_ignoring_400(stream_name: str) -> None:
    requester = _load_streams()[stream_name]["retriever"]["requester"]

    assert requester["error_handler"] == _EXPECTED_ERROR_HANDLER
