# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

import pytest
from jsonschema import Draft7Validator

from airbyte_cdk.test.mock_http import HttpMocker

from .helpers import PAGE_SIZE, START_DATE_PARAM, discover_schema, json_response, read_stream, request


_ORDER = {
    "orderId": 1,
    "modifyDate": "2024-03-01T10:00:00.0000000",
    "paymentMethod": "CreditCard",
    "userId": "1f2e3d4c-0000-4000-8000-000000000001",
    "shipByDate": "2024-03-04T00:00:00.0000000",
}
_PRODUCT = {
    "productId": 2,
    "customsValue": 12.5,
    "noCustoms": False,
    "internalNotes": "Fragile",
    "upc": "012345678905",
    "defaultCost": 3.25,
    "length": 10.0,
    "width": 4.0,
    "height": 2.0,
    "weightOz": 8.0,
    "fulfillmentSku": "F-SKU",
    "productType": "Default",
    "warehouseLocation": "A1",
    "defaultCarrierCode": "ups",
    "defaultServiceCode": "ups_ground",
    "defaultPackageCode": "package",
    "defaultIntlCarrierCode": "fedex",
    "defaultIntlServiceCode": "fedex_international_priority",
    "defaultIntlPackageCode": "fedex_envelope",
    "defaultConfirmation": "none",
    "defaultIntlConfirmation": "signature",
    "customsDescription": "Mug",
    "customsTariffNo": "6912.00",
    "customsCountryCode": "US",
    "modifyDate": "2024-03-01T10:00:00.0000000",
    "productCategory": {"categoryId": 1, "name": "Kitchen"},
    "tags": [{"tagId": 8362, "name": "Backorder"}],
}
_FULFILLMENT = {
    "fulfillmentId": 3,
    "createDate": "2024-03-01T10:00:00.0000000",
    "notifyErrorMessage": "Marketplace rejected tracking number",
}


@pytest.mark.parametrize(
    "stream_name, query_params, record",
    [
        ("orders", {"sortBy": "ModifyDate", "sortDir": "ASC", "modifyDateStart": START_DATE_PARAM}, _ORDER),
        ("products", {"sortBy": "CreateDate", "sortDir": "ASC"}, _PRODUCT),
        ("fulfillments", {"sortBy": "CreateDate", "sortDir": "ASC", "createDateStart": START_DATE_PARAM}, _FULFILLMENT),
    ],
)
def test_vendor_documented_fields_are_emitted_declared_and_valid(stream_name: str, query_params: Dict[str, str], record: Dict[str, Any]) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            request(stream_name, {**query_params, "page": "1", "pageSize": str(PAGE_SIZE)}),
            json_response({stream_name: [record], "page": 1, "pages": 1}),
        )

        output = read_stream(stream_name)

    schema = discover_schema(stream_name)
    [emitted] = [r.record.data for r in output.records]
    assert emitted == record
    assert set(emitted) - set(schema["properties"]) == set()
    assert list(Draft7Validator(schema).iter_errors(emitted)) == []
