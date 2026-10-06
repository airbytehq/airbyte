# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the `item_collection` stream.

Dataset items have no fixed shape, so each raw item returned by
`GET /v2/datasets/{dataset_id}/items` is emitted wrapped as `{"data": <item>}`.
These tests pin that record output and the offset/limit pagination.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest import TestCase

import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import _YAML_FILE_PATH, get_source


_STREAM_NAME = "item_collection"
_DATASET_ID = "dataset-id"
_ITEMS_URL = f"https://api.apify.com/v2/datasets/{_DATASET_ID}/items"
_PAGE_SIZE = 50

_CONFIG = {"token": "apify_api_token", "dataset_id": _DATASET_ID}


def _request(offset: Optional[int] = None) -> HttpRequest:
    query_params = {"limit": str(_PAGE_SIZE)}
    if offset is not None:
        query_params["offset"] = str(offset)
    return HttpRequest(_ITEMS_URL, query_params=query_params, headers={"Authorization": "Bearer apify_api_token"})


def _response(items: List[Any]) -> HttpResponse:
    return HttpResponse(body=json.dumps(items), status_code=200)


def _item(index: int) -> Dict[str, Any]:
    return {
        "url": f"https://example.com/page/{index}",
        "title": f"Page {index}",
        "rank": index,
        "score": index / 3,
        "visited": index % 2 == 0,
        "metadata": {"tags": ["a", "b"], "author": None, "nested": {"depth": [1, {"x": "y"}]}},
    }


def _read() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return read(get_source(config=_CONFIG), _CONFIG, catalog)


class TestItemCollectionStream(TestCase):
    @HttpMocker()
    def test_paginates_with_offset_and_wraps_each_item_under_data(self, http_mocker: HttpMocker) -> None:
        first_page = [_item(i) for i in range(_PAGE_SIZE)]
        second_page = [_item(i) for i in range(_PAGE_SIZE, _PAGE_SIZE + 3)]
        http_mocker.get(_request(), _response(first_page))
        http_mocker.get(_request(offset=_PAGE_SIZE), _response(second_page))

        output = _read()

        assert not output.errors
        assert [record.record.data for record in output.records] == [{"data": item} for item in first_page + second_page]

    @HttpMocker()
    def test_items_with_unusual_shapes_are_wrapped_unchanged(self, http_mocker: HttpMocker) -> None:
        items = [
            {"data": {"already": "wrapped"}, "other": 1},
            {"a/b": 1, "*": 2, "[0]": 3, "**": {"/": "slash"}},
            {"template": "{{ 1 + 1 }}", "jinja_block": "{% if true %}x{% endif %}"},
            {"quotes": 'it\'s "quoted"', "newline": "line1\nline2", "backslash": "C:\\path"},
            {"unicode": "Žluťoučký kůň 🐎", "emoji_key_🔑": "v"},
            {"big_int": 12345678901234567890, "negative": -1.5e-10, "zero": 0, "false": False, "null": None},
            {"empty_list": [], "empty_dict": {}, "list_of_lists": [[1, 2], [3]]},
            {"True": "true", "None": "none", "1": 1},
        ]
        http_mocker.get(_request(), _response(items))

        output = _read()

        assert not output.errors
        assert [record.record.data for record in output.records] == [{"data": item} for item in items]

    @HttpMocker()
    def test_empty_items_are_skipped(self, http_mocker: HttpMocker) -> None:
        # DpathExtractor drops falsy items; this pins the pre-existing behavior.
        items = [{"id": 1}, {}, {"id": 2}]
        http_mocker.get(_request(), _response(items))

        output = _read()

        assert [record.record.data for record in output.records] == [{"data": {"id": 1}}, {"data": {"id": 2}}]

    @HttpMocker()
    def test_large_item_is_wrapped_unchanged(self, http_mocker: HttpMocker) -> None:
        item = {"text": "x" * 400_000, "markdown": "# title\n" * 1000, "links": [f"https://e.com/{i}" for i in range(1000)]}
        http_mocker.get(_request(), _response([item]))

        output = _read()

        assert [record.record.data for record in output.records] == [{"data": item}]

    @HttpMocker()
    def test_empty_dataset_emits_no_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_request(), _response([]))

        output = _read()

        assert not output.errors
        assert output.records == []


def test_manifest_does_not_reference_custom_components() -> None:
    manifest_text = Path(_YAML_FILE_PATH).read_text()
    assert "source_declarative_manifest.components" not in manifest_text
    assert "CustomRecordExtractor" not in manifest_text
    assert not (Path(_YAML_FILE_PATH).parent / "components.py").exists()
    yaml.safe_load(manifest_text)
