# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List, Optional

import pytest

from airbyte_cdk.test.mock_http import HttpMocker

from .helpers import json_response, read_stream, request


@pytest.mark.parametrize(
    "stream_name, path, query_params, body, primary_key, expected_ids",
    [
        ("users", "users", {"showInactive": "true"}, [{"userId": "u1"}, {"userId": "u2"}], "userId", ["u1", "u2"]),
        ("stores", "stores", {"showInactive": "true"}, [{"storeId": 11}, {"storeId": 12}], "storeId", [11, 12]),
        ("carriers", "carriers", None, [{"shippingProviderId": 1, "code": "ups"}], "shippingProviderId", [1]),
        ("warehouses", "warehouses", None, [{"warehouseId": 21}, {"warehouseId": 22}], "warehouseId", [21, 22]),
        ("webhooks", "webhooks", None, {"webhooks": [{"WebHookID": 31}, {"WebHookID": 32}]}, "WebHookID", [31, 32]),
        ("marketplaces", "stores/marketplaces", None, [{"name": "Amazon", "marketplaceId": 2}], "marketplaceId", [2]),
        (
            "tags",
            "accounts/listtags",
            None,
            [{"tagId": 8362, "name": "Backorder", "color": "#800080"}, {"tagId": 8324, "name": "Canada", "color": "#ff0000"}],
            "tagId",
            [8362, 8324],
        ),
    ],
)
def test_unpaginated_stream_reads_records_from_single_request(
    stream_name: str,
    path: str,
    query_params: Optional[Dict[str, str]],
    body: Any,
    primary_key: str,
    expected_ids: List[Any],
) -> None:
    with HttpMocker() as http_mocker:
        http_request = request(path, query_params)
        http_mocker.get(http_request, json_response(body))

        output = read_stream(stream_name)

        assert [record.record.data[primary_key] for record in output.records] == expected_ids
        assert output.errors == []
        http_mocker.assert_number_of_calls(http_request, 1)
