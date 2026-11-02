import json

import pytest
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


CONFIG = {"api_key": "test"}
BASE_URL = "https://api.huntr.co/org"
STREAM_NAMES = ("members", "candidates")
EXPECTED_ERROR_HANDLER = {
    "type": "DefaultErrorHandler",
    "backoff_strategies": [{"type": "ConstantBackoffStrategy", "backoff_time_in_seconds": 5}],
    "response_filters": [{"type": "HttpResponseFilter", "action": "IGNORE"}],
}


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("backoff._sync.time.sleep", lambda *_args, **_kwargs: None)


def _resolved_manifest():
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _read_stream(stream_name: str):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(CONFIG), CONFIG, catalog)


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = _resolved_manifest()
    composite_handlers = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "Composite" + "ErrorHandler":
                composite_handlers.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(manifest)

    assert not composite_handlers


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_streams_use_expected_default_error_handler(stream_name: str) -> None:
    manifest = _resolved_manifest()

    error_handler = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]

    assert error_handler == EXPECTED_ERROR_HANDLER


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_successful_response_yields_one_record(stream_name: str) -> None:
    request = HttpRequest(url=f"{BASE_URL}/{stream_name}", query_params=ANY_QUERY_PARAMS)
    response = HttpResponse(json.dumps({"data": [{"id": "1"}], "next": None}), status_code=200)

    with HttpMocker() as http_mocker:
        http_mocker.get(request, response)

        output = _read_stream(stream_name)

    assert len(output.records) == 1
    assert output.errors == []


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_server_error_is_retried_then_succeeds(stream_name: str) -> None:
    request = HttpRequest(url=f"{BASE_URL}/{stream_name}", query_params=ANY_QUERY_PARAMS)
    responses = [
        HttpResponse('{"error": "server error"}', status_code=500),
        HttpResponse(json.dumps({"data": [{"id": "1"}], "next": None}), status_code=200),
    ]

    with HttpMocker() as http_mocker:
        http_mocker.get(request, responses)

        output = _read_stream(stream_name)

    assert len(output.records) == 1
    assert output.errors == []
    http_mocker.assert_number_of_calls(request, 2)
