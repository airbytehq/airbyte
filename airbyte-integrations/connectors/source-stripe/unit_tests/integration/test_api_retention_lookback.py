#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import freezegun
import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath, create_record_builder, create_response_builder, find_template
from airbyte_cdk.test.state_builder import StateBuilder
from integration.config import ConfigBuilder
from integration.pagination import StripePaginationStrategy
from integration.request_builder import StripeRequestBuilder


_STREAM_NAME = "customers"
_NOW = datetime.now(timezone.utc)
_ACCOUNT_ID = "account_id"
_CLIENT_SECRET = "client_secret"


def _config(lookback_window_days: int) -> Dict[str, Any]:
    return (
        ConfigBuilder()
        .with_start_date(_NOW - timedelta(days=60))
        .with_account_id(_ACCOUNT_ID)
        .with_client_secret(_CLIENT_SECRET)
        .with_lookback_window_in_days(lookback_window_days)
        .with_api_retention_streams([_STREAM_NAME])
        .build()
    )


def _state(cursor_age_in_days: int) -> Any:
    cursor_value = int((_NOW - timedelta(days=cursor_age_in_days)).timestamp())
    return StateBuilder().with_stream_state(_STREAM_NAME, {"updated": cursor_value}).build()


def _events_response():
    return (
        create_response_builder(find_template("events", __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy())
        .with_record(
            create_record_builder(
                find_template("events", __file__),
                FieldPath("data"),
                record_id_path=FieldPath("id"),
                record_cursor_path=FieldPath("created"),
            )
        )
        .build()
    )


def _customers_response():
    return (
        create_response_builder(
            find_template("customers_expand_data_source", __file__), FieldPath("data"), pagination_strategy=StripePaginationStrategy()
        )
        .with_record(
            create_record_builder(
                find_template("customers_expand_data_source", __file__),
                FieldPath("data"),
                record_id_path=FieldPath("id"),
                record_cursor_path=FieldPath("created"),
            )
        )
        .build()
    )


@pytest.mark.parametrize(
    "lookback_window_days,cursor_age_in_days,expected_endpoint",
    [
        pytest.param(0, 25, "events", id="no_lookback_cursor_within_30_days_stays_incremental"),
        pytest.param(0, 31, "customers", id="no_lookback_cursor_older_than_30_days_falls_back_to_full_refresh"),
        pytest.param(7, 25, "customers", id="lookback_7_cursor_older_than_23_days_falls_back_to_full_refresh"),
        pytest.param(7, 20, "events", id="lookback_7_cursor_within_23_days_stays_incremental"),
        pytest.param(30, 1, "customers", id="lookback_30_always_falls_back_to_full_refresh"),
        pytest.param(35, 1, "customers", id="lookback_greater_than_30_capped_at_zero_falls_back_to_full_refresh"),
    ],
)
@freezegun.freeze_time(_NOW.isoformat())
def test_api_retention_period_accounts_for_lookback_window(
    lookback_window_days: int, cursor_age_in_days: int, expected_endpoint: str
) -> None:
    """
    Streams opted into `api_retention_streams` sync incrementally through the `/v1/events` endpoint, which only
    retains 30 days of data. Since `lookback_window_days` shifts the query window back in time, the effective
    retention threshold is `30 - lookback_window_days` days (floored at 0): a cursor older than that must trigger
    a full refresh through the entity endpoint instead of an incremental read through `/v1/events`.
    """
    with HttpMocker() as http_mocker:
        if expected_endpoint == "events":
            http_mocker.get(
                StripeRequestBuilder.events_endpoint(_ACCOUNT_ID, _CLIENT_SECRET).with_any_query_params().build(),
                _events_response(),
            )
        else:
            http_mocker.get(
                StripeRequestBuilder.customers_endpoint(_ACCOUNT_ID, _CLIENT_SECRET).with_any_query_params().build(),
                _customers_response(),
            )

        config = _config(lookback_window_days)
        state = _state(cursor_age_in_days)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()

        output = read(get_source(config, state), config, catalog, state)

        assert len(output.records) == 1
