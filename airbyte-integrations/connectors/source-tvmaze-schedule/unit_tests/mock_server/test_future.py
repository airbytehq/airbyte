# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import read_stream

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize("empty", [False, True])
def test_single_full_schedule_request(http_mocker: HttpMocker, empty: bool) -> None:
    request = HttpRequest("https://api.tvmaze.com/schedule/full", query_params={})
    records = [] if empty else [{"id": 3, "airdate": "2024-02-01", "name": "Future episode"}]
    http_mocker.get(request, HttpResponse(json.dumps(records)))

    output = read_stream("future", SyncMode.full_refresh)

    assert output.errors == []
    assert [record.record.data for record in output.records] == records
    http_mocker.assert_number_of_calls(request, 1)
