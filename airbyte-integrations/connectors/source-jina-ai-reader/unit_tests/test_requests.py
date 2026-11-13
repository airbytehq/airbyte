# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock
from source_jina_ai_reader.source import SourceJinaAiReader

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_API_KEY = "test_api_key"
_RECORDS = [{"title": "Example", "url": "https://example.com", "content": "Example content"}]


@pytest.mark.parametrize(
    ("stream_name", "config", "expected_url"),
    [
        (
            "search",
            {
                "search_prompt": "What%20is%20AI",
                "read_prompt": "https://example.com",
                "gather_links": True,
                "gather_images": True,
            },
            "https://s.jina.ai/What%20is%20AI",
        ),
        (
            "reader",
            {
                "search_prompt": "What%20is%20AI",
                "read_prompt": "https://example.com",
                "gather_links": True,
                "gather_images": True,
            },
            "https://r.jina.ai/https://example.com",
        ),
    ],
)
@pytest.mark.parametrize("with_api_key", [True, False])
def test_read_request_headers(stream_name, config, expected_url, with_api_key):
    config = dict(config)
    if with_api_key:
        config["api_key"] = _API_KEY

    with requests_mock.Mocker() as mocker:
        request = mocker.get(expected_url, json={"data": _RECORDS})
        source = SourceJinaAiReader(config=config, catalog=None, state=None)
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

    assert len(output.records) == len(_RECORDS)
    assert request.call_count == 1
    assert request.request_history[0].url == expected_url
    if with_api_key:
        assert request.request_history[0].headers["Authorization"] == f"Bearer {_API_KEY}"
    else:
        assert "Authorization" not in request.request_history[0].headers
    assert request.request_history[0].headers["Accept"] == "application/json"
    assert request.request_history[0].headers["X-With-Links-Summary"] == "True"
    assert request.request_history[0].headers["X-With-Images-Summary"] == "True"
