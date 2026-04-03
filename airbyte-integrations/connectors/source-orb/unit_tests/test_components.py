#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, List, MutableMapping

import pytest
from requests import Response


def _create_response(body: Any) -> Response:
    response = Response()
    response._content = json.dumps(body).encode("utf-8")
    return response


# ---------------------------------------------------------------------------
# SubscriptionUsageRecordExtractor tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "response_body, expected_records",
    [
        pytest.param(
            {
                "data": [
                    {
                        "billable_metric": {"name": "API Calls", "id": "metric_1"},
                        "usage": [
                            {
                                "quantity": 10,
                                "timeframe_start": "2024-01-01T00:00:00Z",
                                "timeframe_end": "2024-01-02T00:00:00Z",
                            },
                            {
                                "quantity": 5,
                                "timeframe_start": "2024-01-02T00:00:00Z",
                                "timeframe_end": "2024-01-03T00:00:00Z",
                            },
                        ],
                    }
                ]
            },
            [
                {
                    "quantity": 10,
                    "timeframe_start": "2024-01-01T00:00:00Z",
                    "timeframe_end": "2024-01-02T00:00:00Z",
                    "billable_metric_name": "API Calls",
                    "billable_metric_id": "metric_1",
                },
                {
                    "quantity": 5,
                    "timeframe_start": "2024-01-02T00:00:00Z",
                    "timeframe_end": "2024-01-03T00:00:00Z",
                    "billable_metric_name": "API Calls",
                    "billable_metric_id": "metric_1",
                },
            ],
            id="multiple_usage_subrecords",
        ),
        pytest.param(
            {
                "data": [
                    {
                        "billable_metric": {"name": "API Calls", "id": "metric_1"},
                        "usage": [
                            {"quantity": 0, "timeframe_start": "2024-01-01T00:00:00Z"},
                            {"quantity": 10, "timeframe_start": "2024-01-02T00:00:00Z"},
                        ],
                    }
                ]
            },
            [
                {
                    "quantity": 10,
                    "timeframe_start": "2024-01-02T00:00:00Z",
                    "billable_metric_name": "API Calls",
                    "billable_metric_id": "metric_1",
                },
            ],
            id="filters_zero_quantity",
        ),
        pytest.param(
            {
                "data": [
                    {
                        "billable_metric": {"name": "Metric A", "id": "m_a"},
                        "usage": [{"quantity": 1, "timeframe_start": "2024-01-01T00:00:00Z"}],
                    },
                    {
                        "billable_metric": {"name": "Metric B", "id": "m_b"},
                        "usage": [{"quantity": 2, "timeframe_start": "2024-01-01T00:00:00Z"}],
                    },
                ]
            },
            [
                {
                    "quantity": 1,
                    "timeframe_start": "2024-01-01T00:00:00Z",
                    "billable_metric_name": "Metric A",
                    "billable_metric_id": "m_a",
                },
                {
                    "quantity": 2,
                    "timeframe_start": "2024-01-01T00:00:00Z",
                    "billable_metric_name": "Metric B",
                    "billable_metric_id": "m_b",
                },
            ],
            id="multiple_data_items",
        ),
        pytest.param(
            {"data": []},
            [],
            id="empty_data",
        ),
        pytest.param(
            {
                "data": [
                    {
                        "billable_metric": {"name": "X", "id": "x"},
                        "usage": [],
                    }
                ]
            },
            [],
            id="empty_usage_array",
        ),
        pytest.param(
            {
                "data": [
                    {
                        "billable_metric": {"name": "X", "id": "x"},
                        "usage": [
                            {"quantity": 0, "timeframe_start": "2024-01-01T00:00:00Z"},
                        ],
                    }
                ]
            },
            [],
            id="all_zero_quantity",
        ),
        pytest.param(
            {
                "data": [
                    {
                        "usage": [
                            {"quantity": 5, "timeframe_start": "2024-01-01T00:00:00Z"},
                        ],
                    }
                ]
            },
            [
                {
                    "quantity": 5,
                    "timeframe_start": "2024-01-01T00:00:00Z",
                    "billable_metric_name": "",
                    "billable_metric_id": "",
                },
            ],
            id="missing_billable_metric",
        ),
        pytest.param(
            {
                "data": [
                    {
                        "billable_metric": {},
                        "usage": [
                            {"quantity": 3, "timeframe_start": "2024-01-01T00:00:00Z"},
                        ],
                    }
                ]
            },
            [
                {
                    "quantity": 3,
                    "timeframe_start": "2024-01-01T00:00:00Z",
                    "billable_metric_name": "",
                    "billable_metric_id": "",
                },
            ],
            id="empty_billable_metric",
        ),
    ],
)
def test_extract_records(components_module, response_body, expected_records):
    SubscriptionUsageRecordExtractor = components_module.SubscriptionUsageRecordExtractor
    extractor = SubscriptionUsageRecordExtractor(
        config={},
        parameters={},
    )

    response = _create_response(response_body)
    records = list(extractor.extract_records(response))

    assert records == expected_records
