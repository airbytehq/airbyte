# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest.mock import patch

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


STREAMS = {
    "photos_search": "/v1/search",
    "photos_curated": "/v1/curated",
    "collection_featured": "/v1/collections/featured",
    "videos_search": "/videos/search",
    "videos_popular": "/videos/popular",
}
CONFIG = {"api_key": "test-key", "query": "ocean", "orientation": "landscape", "size": "large", "locale": "en-US", "color": "blue"}


def test_default_error_handlers(manifest: dict) -> None:
    assert "Composite" + "ErrorHandler" not in str(manifest)
    streams = [*manifest["definitions"]["streams"].values(), *manifest["streams"]]
    assert len(streams) == 10
    for stream in streams:
        assert stream["retriever"]["requester"]["error_handler"] == {
            "type": "DefaultErrorHandler",
            "response_filters": [{"type": "HttpResponseFilter", "http_codes": [500], "action": "FAIL"}],
        }


@pytest.mark.parametrize("stream_name", STREAMS)
@pytest.mark.parametrize("status_code", [200, 429, 500])
def test_http_error_handling(source: YamlDeclarativeSource, stream_name: str, status_code: int) -> None:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    request = HttpRequest(f"https://api.pexels.com{STREAMS[stream_name]}", query_params=ANY_QUERY_PARAMS)
    responses = [HttpResponse("{}", status_code)]
    if status_code == 429:
        responses.append(HttpResponse("{}", 200))
    with patch("time.sleep") as sleep, HttpMocker() as http_mocker:
        http_mocker.get(request, responses)
        output = read(source, CONFIG, catalog)
        http_mocker.assert_number_of_calls(request, 2 if status_code == 429 else 1)
        assert bool(output.errors) == (status_code == 500)
        if status_code == 429:
            sleep.assert_called()
        else:
            sleep.assert_not_called()
        if status_code == 500:
            assert any("500" in str(error.trace.error) for error in output.errors)
