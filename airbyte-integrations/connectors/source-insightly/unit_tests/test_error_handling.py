# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest.mock import patch

from conftest import MANIFEST_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models import DefaultErrorHandler
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


CONFIG = {"token": "test-token", "nothing": "", "start_date": "2024-01-01T00:00:00Z"}


def test_403_is_ignored() -> None:
    catalog = CatalogBuilder().with_stream("activity_sets", SyncMode.full_refresh).build()
    request = HttpRequest("https://api.na1.insightly.com/v3.1/ActivitySets", query_params=ANY_QUERY_PARAMS)
    with HttpMocker() as mocker, patch("time.sleep") as sleep:
        mocker.get(request, HttpResponse('{}', 403))
        output = read(get_source(CONFIG, catalog), CONFIG, catalog)
        assert output.records == []
        assert output.errors == []
        mocker.assert_number_of_calls(request, 1)
        sleep.assert_not_called()


def test_429_is_retried_with_six_second_backoff() -> None:
    catalog = CatalogBuilder().with_stream("activity_sets", SyncMode.full_refresh).build()
    source = get_source(CONFIG, catalog)
    handler = source.resolved_manifest["streams"][0]["retriever"]["requester"]["error_handler"]
    filters = handler.get("response_filters", [])
    if handler["type"] == "CompositeErrorHandler":
        filters = [response_filter for child in handler["error_handlers"] for response_filter in child["response_filters"]]
    assert any(response_filter.get("http_codes") == [429] and response_filter["action"] == "RETRY" for response_filter in filters)
    backoff_handler = handler if handler["type"] == "DefaultErrorHandler" else handler["error_handlers"][1]
    component = ModelToComponentFactory().create_component(DefaultErrorHandler, backoff_handler, CONFIG)
    assert component.backoff_time(None, attempt_count=1) == 6
    request = HttpRequest("https://api.na1.insightly.com/v3.1/ActivitySets", query_params=ANY_QUERY_PARAMS)
    with HttpMocker() as mocker, patch("time.sleep") as sleep:
        mocker.get(request, [HttpResponse('{}', 429), HttpResponse('[{"ACTIVITYSET_ID": 1}]')])
        output = read(source, CONFIG, catalog)
        assert output.errors == []
        assert [message.record.data for message in output.records] == [{"ACTIVITYSET_ID": 1}]
        mocker.assert_number_of_calls(request, 2)
        assert [call.args[0] for call in sleep.call_args_list] == [7, 0]


def test_manifest_has_no_composite_error_handler() -> None:
    assert "CompositeErrorHandler" not in MANIFEST_PATH.read_text()
