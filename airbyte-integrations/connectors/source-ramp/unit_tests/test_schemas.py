# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the declared date and timestamp types:

- the 13 fields that 1.0.0 typed declare the format matching the values Ramp returns
- the three date-like fields Ramp does not return in ISO 8601 stay plain strings
- every top-level `*_at` field of every stream is declared as a timestamp
- every other top-level field named like a date is declared as a date or a timestamp
"""

import functools
import re

import pytest
from _helpers import CONFIG, get_source


NON_ISO_DATE_FIELDS = [
    ("cards", "expiration"),
    ("business_balance", "next_billing_date"),
    ("business_balance", "prev_billing_date"),
]

# Matches `created_at`, `user_transaction_time`, `promise_date` and `last_date_to_terminate`.
DATE_FIELD_NAME = re.compile(r"(_at|_time|_date)$|(^|_)date(_|$)")


@functools.cache
def _schemas() -> dict:
    return {stream.name: stream.get_json_schema() for stream in get_source(CONFIG).streams(CONFIG)}


TYPED_IN_1_0_0 = [
    ("cards", "created_at", "date-time"),
    ("transactions", "accounting_date", "date-time"),
    ("transactions", "settlement_date", "date-time"),
    ("transactions", "synced_at", "date-time"),
    ("transactions", "updated_at", "date-time"),
    ("transactions", "user_transaction_time", "date-time"),
    ("reimbursements", "accounting_date", "date-time"),
    ("reimbursements", "approved_at", "date-time"),
    ("reimbursements", "created_at", "date-time"),
    ("reimbursements", "submitted_at", "date-time"),
    ("reimbursements", "synced_at", "date-time"),
    ("reimbursements", "updated_at", "date-time"),
    ("reimbursements", "transaction_date", "date"),
]


@pytest.mark.parametrize("stream_name, field, expected_format", TYPED_IN_1_0_0)
def test_date_fields_declare_their_format(stream_name, field, expected_format):
    """Ramp returns these as ISO 8601 timestamps, or a date for `transaction_date`."""
    prop = _schemas()[stream_name]["properties"][field]
    assert prop["type"] == ["string", "null"]
    assert prop["format"] == expected_format
    # Without a time zone, the destination column type would change a second time.
    assert prop.get("airbyte_type") != "timestamp_without_timezone"


@pytest.mark.parametrize("stream_name, field", NON_ISO_DATE_FIELDS)
def test_non_iso_date_fields_stay_strings(stream_name, field):
    """`expiration` is MMYY and the billing dates are MM/DD/YYYY, so a `format` would reject their values."""
    prop = _schemas()[stream_name]["properties"][field]
    assert prop["type"] == ["string", "null"]
    assert "format" not in prop


def test_every_at_field_is_a_timestamp():
    """A new `*_at` field must be typed when it is declared; typing it later is a breaking change."""
    untyped = [
        f"{stream_name}.{field}"
        for stream_name, schema in _schemas().items()
        for field, prop in schema["properties"].items()
        if field.endswith("_at") and prop.get("format") != "date-time"
    ]
    assert untyped == []


def test_every_date_named_field_is_typed():
    """Names like `settlement_date` or `user_transaction_time` hold dates too, and typing one later is a breaking change."""
    untyped = [
        f"{stream_name}.{field}"
        for stream_name, schema in _schemas().items()
        for field, prop in schema["properties"].items()
        if "string" in prop.get("type", [])
        and DATE_FIELD_NAME.search(field)
        and (stream_name, field) not in NON_ISO_DATE_FIELDS
        and prop.get("format") not in ("date", "date-time")
    ]
    assert untyped == []
