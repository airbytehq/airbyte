# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


def _request(page: int) -> HttpRequest:
    headers = {"token": "dummy-api-key", "X-request-sender": "Airbyte"}
    if page > 1:
        headers["X-page"] = str(page - 1)
    return HttpRequest(
        url="https://api.serpstat.com/v4/",
        headers=headers,
        body={
            "id": "2026-11-09 00:00:00+00:00",
            "method": "SerpstatDomainProcedure.getDomainsHistory",
            "params": {
                "se": "g_us",
                "page": page,
                "size": 1,
                "sort": {"date": "desc"},
                "domain": "example.com",
                "during_all_time": True,
            },
        },
    )


def _response(page: int, record: dict) -> HttpResponse:
    return HttpResponse(body=json.dumps({"result": {"data": [record], "summary_info": {"page": page}}}), status_code=200)


@freezegun.freeze_time("2026-11-09T00:00:00Z")
def test_domain_history_paginates_and_stops_at_configured_page() -> None:
    config = {"api_key": "dummy-api-key", "domain": "example.com", "region_id": "g_us", "page_size": 1, "pages_to_fetch": 2}
    records = [
        {"date": "2026-11-08", "domain": "example.com", "keywords": 15, "traff": 120},
        {"date": "2026-11-07", "domain": "example.com", "keywords": 12, "traff": 100},
    ]
    first_request, second_request = _request(1), _request(2)
    catalog = CatalogBuilder().with_stream("Domain history", SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        http_mocker.post(first_request, _response(1, records[0]))
        http_mocker.post(second_request, _response(2, records[1]))
        output = read(get_source(config, catalog), config=config, catalog=catalog)

        assert output.errors == []
        assert [message.record.data for message in output.records] == records
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(second_request, 1)
