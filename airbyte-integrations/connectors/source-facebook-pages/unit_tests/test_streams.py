#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock as rm
import yaml
from source_facebook_pages.source import SourceFacebookPages

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    FailureType,
    SyncMode,
)


CONFIG = {"page_id": "1", "access_token": "token"}
ACCESS_TOKEN_URL = "https://graph.facebook.com/1?fields=access_token&access_token=token"
PAGE_URL = "https://graph.facebook.com/v24.0/1"
FEED_URL = "https://graph.facebook.com/v24.0/1/feed"
MANIFEST_PATH = Path(__file__).parents[1] / "source_facebook_pages" / "manifest.yaml"


def _make_catalog(stream_name, selected_fields):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=stream_name,
                    json_schema={
                        "type": "object",
                        "properties": {field: {"type": ["string", "null"]} for field in selected_fields},
                    },
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )


def _get_fields_from_request(request_history, target_url_path):
    for req in request_history:
        parsed = urlparse(req.url)
        if parsed.path == target_url_path:
            params = parse_qs(parsed.query)
            if "fields" in params:
                return params["fields"][0]
    return None


@pytest.mark.parametrize(
    "stream_name,selected_fields,mock_url,mock_response,url_path",
    [
        pytest.param(
            "page",
            ["id", "name", "category"],
            PAGE_URL,
            {"id": "1", "name": "Test Page", "category": "Business"},
            "/v24.0/1",
            id="page_stream_filters_to_3_fields",
        ),
        pytest.param(
            "post",
            ["id", "message", "created_time"],
            FEED_URL,
            {"data": [{"id": "1_123", "message": "Hello", "created_time": "2024-01-01T00:00:00+0000"}], "paging": {}},
            "/v24.0/1/feed",
            id="post_stream_filters_to_3_fields",
        ),
        pytest.param(
            "page",
            ["id", "fan_count"],
            PAGE_URL,
            {"id": "1", "fan_count": "100"},
            "/v24.0/1",
            id="page_stream_filters_to_2_fields",
        ),
    ],
)
def test_stream_filters_fields_to_configured_catalog(stream_name, selected_fields, mock_url, mock_response, url_path):
    catalog = _make_catalog(stream_name, selected_fields)

    with rm.Mocker() as m:
        m.get(ACCESS_TOKEN_URL, json={"access_token": "access"})
        m.get(mock_url, json=mock_response)

        source = SourceFacebookPages(catalog=catalog, config=CONFIG)
        logger = logging.getLogger("test")
        list(source.read(logger, CONFIG, catalog))

        raw_fields = _get_fields_from_request(m.request_history, url_path)
        assert raw_fields is not None, f"Expected a request to {url_path} with fields parameter"
        requested_fields = set(raw_fields.split(","))
        assert requested_fields == set(selected_fields), f"Expected fields {set(selected_fields)}, got {requested_fields}"


def test_without_catalog_at_init_requests_all_fields():
    with rm.Mocker() as m:
        m.get(ACCESS_TOKEN_URL, json={"access_token": "access"})
        m.get(PAGE_URL, json={"id": "1", "name": "Test Page"})

        source = SourceFacebookPages(config=CONFIG)
        catalog = _make_catalog("page", ["id"])
        logger = logging.getLogger("test")
        list(source.read(logger, CONFIG, catalog))

        raw_fields = _get_fields_from_request(m.request_history, "/v24.0/1")
        assert raw_fields is not None, "Expected a request to /v24.0/1 with fields parameter"
        requested_fields = raw_fields.split(",")
        assert (
            len(requested_fields) > 3
        ), f"Without catalog at init, expected all fields to be requested, but got only {len(requested_fields)}"


REQUIRED_PERMISSIONS = (
    "pages_read_engagement",
    "pages_read_user_content",
    "pages_show_list",
    "read_insights",
    "catalog_management",
)


def test_facebook_app_approval_error_is_config_error():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    response_filter = manifest["definitions"]["requester"]["error_handler"]["response_filters"][0]

    assert response_filter["error_message_contains"] == "This application has not been approved to use this API"
    assert response_filter["failure_type"] == FailureType.config_error.value
    assert response_filter["error_message"].startswith(
        "The application used to create the Facebook access token has not been approved to use this API."
    )
    for permission in REQUIRED_PERMISSIONS:
        assert permission in response_filter["error_message"]


def test_facebook_permission_error_is_config_error():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    response_filter = manifest["definitions"]["requester"]["error_handler"]["response_filters"][1]

    assert response_filter["error_message_contains"] == "Requires"
    assert response_filter["failure_type"] == FailureType.config_error.value
    assert "Meta reported: {{ response.error.message }}" in response_filter["error_message"]
    for permission in REQUIRED_PERMISSIONS:
        assert permission in response_filter["error_message"]
