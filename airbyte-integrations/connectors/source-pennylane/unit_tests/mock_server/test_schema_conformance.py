# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Fields the v1 API returns on `customer_invoices` and `customers` must be declared
in the discovered schema with types that accept the values the API sends.
"""

from typing import Any, Dict

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.helpers import discover_schema, read_stream
from mock_server.request_builder import STREAMS, list_request, list_response, record


_JSON_TYPES = {"object": dict, "string": str, "boolean": bool, "integer": int, "number": (int, float), "array": list}
_STREAMS_BY_NAME = {stream.name: stream for stream in STREAMS}

_CUSTOMER_INVOICE_FIELDS: Dict[str, Any] = {
    "billing_subscription": {"id": 42, "v2_id": 4242},
    "imputation_dates": {"start_date": "2024-01-01", "end_date": "2024-01-31"},
    "transactions_reference": {"banking_provider": "bank", "provider_field_name": "label", "provider_field_value": "INV-1"},
    "is_estimate": False,
}
_CUSTOMER_FIELDS: Dict[str, Any] = {
    "notes": "VIP customer",
    "billing_iban": "FR7630006000011234567890189",
    "gender": "madam",
}


def _accepts(schema: Dict[str, Any], value: Any) -> bool:
    declared = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
    if value is None:
        return "null" in declared
    if isinstance(value, bool):
        return "boolean" in declared
    return any(isinstance(value, _JSON_TYPES[json_type]) for json_type in declared if json_type in _JSON_TYPES)


@freezegun.freeze_time("2024-06-01T00:00:00Z")
@pytest.mark.parametrize(
    "stream_name, vendor_fields",
    [("customer_invoices", _CUSTOMER_INVOICE_FIELDS), ("customers", _CUSTOMER_FIELDS)],
)
def test_emitted_vendor_fields_are_declared_with_matching_types(stream_name: str, vendor_fields: Dict[str, Any]) -> None:
    stream = _STREAMS_BY_NAME[stream_name]
    config = ConfigBuilder().build()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            list_request(stream, page=1, updated_since="2024-01-01T00:00:00.000000Z"),
            list_response(stream, [record(stream, "1", **vendor_fields)], current_page=1, total_pages=1),
        )
        output = read_stream(stream.name, SyncMode.full_refresh, config)

    assert [error.trace.error.message for error in output.errors] == []
    properties = discover_schema(stream.name, config)["properties"]
    emitted = output.records[0].record.data
    for field_name in vendor_fields:
        assert field_name in properties, f"{stream_name}.{field_name} is emitted but not declared"
        assert _accepts(properties[field_name], emitted[field_name]), f"{stream_name}.{field_name}={emitted[field_name]!r}"
    for sub_field, value in vendor_fields.get("imputation_dates", {}).items():
        assert _accepts(properties["imputation_dates"]["properties"][sub_field], value)
