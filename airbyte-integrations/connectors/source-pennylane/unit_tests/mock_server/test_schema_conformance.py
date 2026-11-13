# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Fields the v1 API returns on `customer_invoices` and `customers` must be declared
in the discovered schema with types that accept the values the API sends.
"""

import re
from typing import Any, Dict, List

import freezegun
import pytest
from jsonschema import Draft7Validator, FormatChecker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.helpers import discover_schema, read_stream
from mock_server.request_builder import STREAMS, list_request, list_response, record


# jsonschema checks `date` out of the box but skips `date-time` unless rfc3339-validator is installed.
_FORMAT_CHECKER = FormatChecker()
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


@_FORMAT_CHECKER.checks("date-time")
def _is_date_time(value: object) -> bool:
    return not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}.*", value) is not None


def _violations(schema: Dict[str, Any], value: Any) -> List[str]:
    """Every way `value` breaks `schema`, nested properties and `format` included."""
    validator = Draft7Validator(schema, format_checker=_FORMAT_CHECKER)
    return [f"{'.'.join(map(str, error.absolute_path)) or '<value>'}: {error.message}" for error in validator.iter_errors(value)]


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
        assert _violations(properties[field_name], emitted[field_name]) == [], f"{stream_name}.{field_name}"
