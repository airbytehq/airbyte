# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


@pytest.mark.parametrize("stream_name,record_count", [("categories", 19), ("distribution_channels", 5)])
@pytest.mark.parametrize("response_kind", ["records", "empty", "unauthorized"])
def test_lookup_stream_requests_list_once(stream_name, record_count, response_kind):
    config = {"api_token": "x"}
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    records = [{"id": str(index), "value": f"lookup-{index}"} for index in range(record_count)] if response_kind == "records" else []
    response = HttpResponse(
        body=json.dumps({"collection": records} if response_kind != "unauthorized" else {"message": "Unauthorized"}),
        status_code=401 if response_kind == "unauthorized" else 200,
    )
    request = HttpRequest(url=f"https://api.simplecast.com/{stream_name}", query_params=ANY_QUERY_PARAMS)

    with HttpMocker() as http_mocker:
        # Repeat the full list, then terminate even if a broken paginator keeps requesting it.
        http_mocker.get(request, [response, response, HttpResponse(body='{"collection": []}', status_code=200)])
        output = read(get_source(config, catalog), config=config, catalog=catalog, expecting_exception=response_kind == "unauthorized")

        assert [message.record.data for message in output.records] == records
        http_mocker.assert_number_of_calls(request, 1)
        assert "offset" not in http_mocker._mocker.request_history[0].qs
        if response_kind == "unauthorized":
            assert output.errors
            assert "Unauthorized" in output.get_formatted_error_message()
        else:
            assert not output.errors
            assert not any(log.log.level == "ERROR" for log in output.logs)
