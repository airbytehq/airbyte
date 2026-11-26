# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""`metrics_overview` reads one unpaginated snapshot per project."""

import json

from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.helpers import read_stream, records_data
from mock_server.request_builder import RevenueCatRequestBuilder
from mock_server.streams import mock_ancestors


_STREAM = "metrics_overview"


def _metric(metric_id: str, value: float) -> dict:
    return {
        "object": "overview_metric",
        "id": metric_id,
        "name": metric_id,
        "description": "",
        "unit": "#",
        "period": "P0D",
        "value": value,
        "last_updated_at": 1735689600000,
        "last_updated_at_iso8601": "2025-01-01T00:00:00Z",
    }


def test_one_request_without_paging_params_per_project_and_records_carry_project_id() -> None:
    with HttpMocker() as http_mocker:
        mock_ancestors(http_mocker, _STREAM, ["proj_a", "proj_b"])
        requests = {}
        for project_id, value in (("proj_a", 1.0), ("proj_b", 2.0)):
            request = RevenueCatRequestBuilder.endpoint(f"/projects/{project_id}/metrics/overview").without_query_params().build()
            body = {"object": "overview_metrics", "metrics": [_metric("active_trials", value), _metric("mrr", value)]}
            http_mocker.get(request, HttpResponse(body=json.dumps(body), status_code=200))
            requests[project_id] = request

        output = read_stream(_STREAM)

    assert output.errors == []
    emitted = sorted((r["project_id"], r["id"], r["value"]) for r in records_data(output))
    assert emitted == [
        ("proj_a", "active_trials", 1.0),
        ("proj_a", "mrr", 1.0),
        ("proj_b", "active_trials", 2.0),
        ("proj_b", "mrr", 2.0),
    ]
    for request in requests.values():
        http_mocker.assert_number_of_calls(request, 1)
