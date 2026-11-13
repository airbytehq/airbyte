# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import pytest
from requests import Response

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


@pytest.mark.parametrize("resource", ["registrations", "sessions"])
@pytest.mark.parametrize("mode", ["initial", "incremental"])
@pytest.mark.parametrize("record_count", [0, 3, 10000, 10001])
def test_transactional_pagination(resource, mode, record_count):
    config = {"api_key": "test-api-key", "start_date": "20250101"}
    catalog = CatalogBuilder().with_stream(f"{resource} {mode}", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).parent.parent / "manifest.yaml"), config=config, catalog=catalog, state=None
    )
    requests = []

    def send(request, **kwargs):
        url = urlparse(request.url)
        assert url.scheme == "https"
        assert url.netloc == "api.opuswatch.nl"
        assert url.path == f"/ext/transactional/{resource}"
        assert request.headers["key"] == config["api_key"]
        params = parse_qs(url.query)
        requests.append(params)
        offset = int(params.get("offset", [0])[0])
        limit = int(params.get("limit", [10000])[0])
        response = Response()
        response.status_code = 200
        response.url = request.url
        response.request = request
        response.headers["Content-Type"] = "application/json"
        response._content = json.dumps({"data": [{"id": i} for i in range(offset, min(offset + limit, record_count))]}).encode()
        return response

    with patch("requests.Session.send", side_effect=send):
        output = read(source, config, catalog)

    assert not output.errors
    assert [message.record.data["id"] for message in output.records] == list(range(record_count))
    assert [int(params.get("offset", [0])[0]) for params in requests] == list(range(0, record_count + 1, 10000))
    for params in requests:
        assert params["limit"] == ["10000"]
        assert params["filter_date_by"] == ["CREATED" if mode == "initial" else "UPDATED"]
        assert params["return_archived"] == ["true"]
        assert params["return_breaks"] == ["true"]
        assert params["return_leaves"] == ["true"]
        if mode == "initial":
            assert params["date"] == [config["start_date"]]
            assert params["days_from_date"] == ["366"]
        else:
            assert params["days_till_date"] == ["2"]
