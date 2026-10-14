# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the `content` stream on `source-coda`.

Verifies that the declarative stream emits one record per page content element
(not the API response envelope) and that records carry their parent identifiers.
"""

from pathlib import Path

import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"
_CONFIG = {"auth_token": "test-token"}
_BASE_URL = "https://coda.io/apis/v1"
_STREAM_NAMES = [
    "docs",
    "permissions",
    "categories",
    "pages",
    "tables",
    "formulas",
    "controls",
    "rows",
    "content",
]


def _get_source():
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=_CONFIG,
        state=StateBuilder().build(),
    )


def _read_content():
    catalog = CatalogBuilder().with_stream("content", SyncMode.full_refresh).build()
    return read(_get_source(), _CONFIG, catalog)


def _mock_parents(mocker):
    mocker.get(
        f"{_BASE_URL}/docs",
        json={"items": [{"id": "doc-1"}], "nextPageLink": ""},
    )
    mocker.get(
        f"{_BASE_URL}/docs/doc-1/pages",
        json={"items": [{"id": "page-1"}], "nextPageLink": ""},
    )


def _content_item(item_id):
    return {
        "id": item_id,
        "type": "paragraph",
        "itemContent": {
            "style": "paragraph",
            "format": "plainText",
            "content": f"Content for {item_id}",
            "lineLevel": 0,
        },
    }


def test_content_is_discoverable_and_existing_streams_remain():
    assert {stream.name for stream in _get_source().streams(_CONFIG)} == set(_STREAM_NAMES)


def test_content_emits_one_record_per_item_with_parent_ids():
    response = {"items": [_content_item("item-1"), _content_item("item-2")], "nextPageLink": ""}

    with requests_mock.Mocker() as mocker:
        _mock_parents(mocker)
        mocker.get(f"{_BASE_URL}/docs/doc-1/pages/page-1/content", json=response)
        output = _read_content()

    records = [message.record.data for message in output.records]
    assert [record["id"] for record in records] == ["item-1", "item-2"]
    assert all(record["doc_id"] == "doc-1" for record in records)
    assert all(record["page_id"] == "page-1" for record in records)


def test_content_follows_next_page_link():
    next_page = f"{_BASE_URL}/docs/doc-1/pages/page-1/content?pageToken=page-2"
    first_response = {
        "items": [_content_item("item-1")],
        "nextPageLink": next_page,
    }
    second_response = {
        "items": [_content_item("item-2")],
        "nextPageLink": "",
    }

    with requests_mock.Mocker() as mocker:
        _mock_parents(mocker)
        mocker.get(
            f"{_BASE_URL}/docs/doc-1/pages/page-1/content",
            [{"json": first_response}, {"json": second_response}],
        )
        output = _read_content()

    assert [message.record.data["id"] for message in output.records] == ["item-1", "item-2"]


def test_content_requests_plain_text_format():
    with requests_mock.Mocker() as mocker:
        _mock_parents(mocker)
        mocker.get(
            f"{_BASE_URL}/docs/doc-1/pages/page-1/content",
            json={"items": [_content_item("item-1")], "nextPageLink": ""},
        )
        _read_content()

        assert "contentformat=plaintext" in mocker.last_request.query
