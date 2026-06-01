# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import yaml


MANIFEST_PATH = Path(__file__).resolve().parent.parent / "manifest.yaml"


@pytest.fixture(scope="module")
def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


def _get_stream_def(manifest, stream_name):
    return manifest["definitions"]["streams"][stream_name]


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("invoices", id="invoices"),
        pytest.param("expenses", id="expenses"),
        pytest.param("creditnotes", id="creditnotes"),
        pytest.param("customer_payments", id="customer_payments"),
        pytest.param("purchase_orders", id="purchase_orders"),
        pytest.param("sales_orders", id="sales_orders"),
    ],
)
def test_updated_financial_streams_use_last_modified_time_cursor(manifest, stream_name):
    incremental_sync = _get_stream_def(manifest, stream_name)["incremental_sync"]

    assert incremental_sync["cursor_field"] == "last_modified_time"
    assert incremental_sync["cursor_datetime_formats"] == ["%Y-%m-%dT%H:%M:%S%z"]
    assert incremental_sync["datetime_format"] == "%Y-%m-%dT%H:%M:%S%z"
    assert incremental_sync["start_time_option"]["field_name"] == "last_modified_time"
    assert "end_time_option" not in incremental_sync


def test_transactions_stream_keeps_date_cursor(manifest):
    incremental_sync = _get_stream_def(manifest, "transactions")["incremental_sync"]

    assert incremental_sync["cursor_field"] == "date"
    assert incremental_sync["start_time_option"]["field_name"] == "date_start"
    assert incremental_sync["end_time_option"]["field_name"] == "date_end"
