# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


def test_plans_records(get_source) -> None:
    config = {"api_key": "test-token", "start_date": "2025-01-01T00:00:00Z", "end_date": "2025-01-02T00:00:00Z"}
    record = {"id": "plan-1", "created_at": "2025-01-01T12:00:00Z", "prices": [{"billable_metric": {"id": "metric-1"}}]}
    request = HttpRequest(
        "https://api.billwithorb.com/v1/plans",
        query_params={"limit": "50", "created_at[gte]": "2025-01-01T00:00:00+00:00", "created_at[lte]": "2025-01-02T00:00:00+00:00"},
    )
    with HttpMocker() as mocker:
        mocker.get(request, HttpResponse(json.dumps({"data": [record]})))
        catalog = CatalogBuilder().with_stream("plans", SyncMode.full_refresh).build()
        output = read(get_source(config, catalog), config, catalog)
        assert [message.record.data for message in output.records] == [record]
        assert not output.errors
        mocker.assert_number_of_calls(request, 1)
