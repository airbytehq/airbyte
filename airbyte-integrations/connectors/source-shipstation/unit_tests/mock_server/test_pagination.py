# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Dict

import pytest

from airbyte_cdk.test.mock_http import HttpMocker

from .helpers import PAGE_SIZE, START_DATE_PARAM, json_response, read_stream, request


_CREATED_ASC = {"sortBy": "CreateDate", "sortDir": "ASC"}


@pytest.mark.parametrize(
    "stream_name, field_path, primary_key, cursor_field, query_params",
    [
        ("customers", "customers", "customerId", None, _CREATED_ASC),
        ("products", "products", "productId", None, _CREATED_ASC),
        ("orders", "orders", "orderId", "modifyDate", {"sortBy": "ModifyDate", "sortDir": "ASC", "modifyDateStart": START_DATE_PARAM}),
        (
            "shipments",
            "shipments",
            "shipmentId",
            "createDate",
            {**_CREATED_ASC, "includeShipmentItems": "true", "createDateStart": START_DATE_PARAM},
        ),
        ("fulfillments", "fulfillments", "fulfillmentId", "createDate", {**_CREATED_ASC, "createDateStart": START_DATE_PARAM}),
    ],
)
def test_full_page_requests_next_page_and_short_page_stops(
    stream_name: str, field_path: str, primary_key: str, cursor_field: str, query_params: Dict[str, str]
) -> None:
    with HttpMocker() as http_mocker:

        def page_records(first_id: int, count: int):
            records = [{primary_key: record_id} for record_id in range(first_id, first_id + count)]
            if cursor_field:
                for record in records:
                    record[cursor_field] = "2024-02-01T08:00:00.0000000"
            return records

        first_page = request(field_path, {**query_params, "page": "1", "pageSize": str(PAGE_SIZE)})
        second_page = request(field_path, {**query_params, "page": "2", "pageSize": str(PAGE_SIZE)})
        http_mocker.get(first_page, json_response({field_path: page_records(1, PAGE_SIZE), "page": 1, "pages": 2}))
        http_mocker.get(second_page, json_response({field_path: page_records(PAGE_SIZE + 1, 2), "page": 2, "pages": 2}))

        output = read_stream(stream_name)

        assert [record.record.data[primary_key] for record in output.records] == list(range(1, PAGE_SIZE + 3))
        assert output.errors == []
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)
