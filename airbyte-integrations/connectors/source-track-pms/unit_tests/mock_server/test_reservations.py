# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from .helpers import read_stream


URL = "https://example.trackhs.com/api/pms/reservations"
PARAMS = {"size": "100", "sortColumn": "id", "updatedSince": "1900-01-01T00:00:00+0000"}


def _page(ids: range) -> HttpResponse:
    records = [{"id": i, "updatedAt": "2024-01-01T00:00:00+0000"} for i in ids]
    return HttpResponse(json.dumps({"_embedded": {"reservations": records}, "scroll": "S"}))


def test_reservations_repeated_scroll_token_reads_every_page_once() -> None:
    scroll_request = HttpRequest(URL, query_params={**PARAMS, "scroll": "S"})
    with HttpMocker() as http_mocker:
        http_mocker.get(HttpRequest(URL, query_params={**PARAMS, "scroll": "1"}), _page(range(1, 101)))
        http_mocker.get(scroll_request, [_page(range(101, 201)), _page(range(201, 251)), _page(range(0))])

        output = read_stream("reservations")

        assert sorted(r.record.data["id"] for r in output.records) == list(range(1, 251))
        http_mocker.assert_number_of_calls(scroll_request, 3)
