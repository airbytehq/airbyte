# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import patch

import yaml
from conftest import _get_manifest_path, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"
_CAMPAIGNS_URL = "https://api.linkrunner.io/api/v1/campaigns"
_CONFIG = {"linkrunner-key": "test-key"}


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())

    def walk(node):
        if isinstance(node, dict):
            forbidden_type = "".join(("Composite", "ErrorHandler"))
            assert node.get("type") != forbidden_type
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(manifest)


def test_campaigns_error_handler_retries_rate_limits_and_server_errors_with_default_backoff() -> None:
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_MANIFEST_PATH.read_text()))
    campaigns = next(stream for stream in manifest["streams"] if stream["name"] == "campaigns")
    error_handler_config = campaigns["retriever"]["requester"]["error_handler"]

    assert error_handler_config["type"] == "DefaultErrorHandler"
    error_handler = DefaultErrorHandler.parse_obj(error_handler_config)
    assert error_handler.backoff_strategies is None
    assert error_handler.dict(exclude_unset=True).get("max_retries") is None
    assert len(error_handler.response_filters) == 1
    response_filter = error_handler.response_filters[0]
    assert response_filter.action.value == "RETRY"
    assert response_filter.http_codes == [429, 500, 502, 503, 504]


def test_campaigns_read_retries_server_error(monkeypatch) -> None:
    monkeypatch.setattr("time.sleep", lambda _: None)
    page_one_request = HttpRequest(
        _CAMPAIGNS_URL,
        query_params={"limit": "100", "filter": "ALL"},
        headers={"linkrunner-key": "test-key"},
    )
    first_page_response = HttpResponse(
        json.dumps({"data": {"campaigns": [{"display_id": "campaign-1"}]}}),
        200,
    )
    catalog = CatalogBuilder().with_stream("campaigns", SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        http_mocker.get(
            page_one_request,
            [
                HttpResponse('{"error":"server error"}', 500),
                first_page_response,
            ],
        )
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert output.errors == []
    assert len(output.records) == 1
    http_mocker.assert_number_of_calls(page_one_request, 2)
