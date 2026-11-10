# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


def page(stream: str, key: str, ids: list[str], next_url: str | None = None) -> HttpResponse:
    return HttpResponse(
        body=json.dumps({stream: [{key: record_id} for record_id in ids], "paging": {"next": next_url} if next_url else {}}),
        status_code=200,
    )


@pytest.mark.parametrize("stream,key", [("jobs", "id"), ("candidates", "id"), ("stages", "slug"), ("recruiters", "id")])
def test_read_follows_next_url_with_page_size(stream: str, key: str) -> None:
    config = {"api_key": "test-token", "account_subdomain": "test-account", "start_date": "20240101T000000Z"}
    url = f"https://test-account.workable.com/spi/v3/{stream}"
    params = {"created_after": config["start_date"], "limit": "100"}
    next_url = f"{url}?created_after={config['start_date']}&limit=100&since_id=second-page"
    first = HttpRequest(url=url, query_params=params, headers={"Authorization": "Bearer test-token"})
    second = HttpRequest(url=next_url, headers={"Authorization": "Bearer test-token"})
    with HttpMocker() as http_mocker:
        http_mocker.get(first, page(stream, key, ["first", "second"], next_url))
        http_mocker.get(second, page(stream, key, ["third"]))
        catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()

        output = read(get_source(config), config=config, catalog=catalog)

        assert output.errors == []
        assert [message.record.data[key] for message in output.records] == ["first", "second", "third"]
        http_mocker.assert_number_of_calls(first, 1)
        http_mocker.assert_number_of_calls(second, 1)
