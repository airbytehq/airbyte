# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import read_stream

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize("country", [None, "", "US", "global"])
@pytest.mark.parametrize("mode,cursor", [(SyncMode.full_refresh, None), (SyncMode.incremental, None), (SyncMode.incremental, "2024-01-02")])
@pytest.mark.parametrize("empty", [False, True])
def test_web_schedule(http_mocker: HttpMocker, country: str | None, mode: SyncMode, cursor: str | None, empty: bool) -> None:
    records = []
    requests = []
    for day in [2] if cursor else [1, 2]:
        date = f"2024-01-0{day}"
        params = {"date": date}
        if country == "global":
            params["country"] = ""
        elif country:
            params["country"] = country
        request = HttpRequest("https://api.tvmaze.com/schedule/web", query_params=params)
        batch = [] if empty else [{"id": day, "airdate": date, "name": f"Web episode {day}"}]
        http_mocker.get(request, HttpResponse(json.dumps(batch)))
        requests.append(request)
        records.extend(batch)

    output = read_stream("web", mode, cursor=cursor, country=country)

    assert output.errors == []
    assert sorted((record.record.data for record in output.records), key=lambda record: record["id"]) == records
    if mode == SyncMode.incremental:
        assert output.most_recent_state.stream_state.airdate == ("2024-01-01" if empty and not cursor else "2024-01-02")
    for request in requests:
        http_mocker.assert_number_of_calls(request, 1)
