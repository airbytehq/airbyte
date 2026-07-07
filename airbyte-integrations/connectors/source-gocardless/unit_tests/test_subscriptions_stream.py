# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Unit tests for the `subscriptions` stream on `source-gocardless`.

Verifies that the new subscriptions stream correctly reads records from
the GoCardless /subscriptions endpoint using the same auth, pagination,
and filtering conventions as the existing streams.
"""

from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"

_CONFIG = {
    "access_token": "sandbox_test_token",
    "gocardless_environment": "sandbox",
    "gocardless_version": "2015-07-06",
    "start_date": "2024-01-01T00:00:00Z",
}

_BASE_URL = "https://api-sandbox.gocardless.com"


def _get_source(config=None):
    config = config or _CONFIG
    catalog = CatalogBuilder().build()
    state = StateBuilder().build()
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=catalog,
        config=config,
        state=state,
    )


def _sync_subscriptions(config=None):
    config = config or _CONFIG
    source = _get_source(config)
    catalog = CatalogBuilder().with_stream("subscriptions", SyncMode.full_refresh).build()
    return read(source, config, catalog)


def _subscription_record(sub_id, **overrides):
    record = {
        "id": sub_id,
        "amount": 1000,
        "app_fee": 50,
        "count": None,
        "created_at": "2024-06-01T12:00:00.000Z",
        "currency": "GBP",
        "day_of_month": 1,
        "end_date": None,
        "interval": 1,
        "interval_unit": "monthly",
        "links": {"mandate": "MD0001"},
        "metadata": {},
        "month": None,
        "name": "Test Subscription",
        "start_date": "2024-06-01",
        "status": "active",
    }
    record.update(overrides)
    return record


def test_subscriptions_stream_exists():
    """The subscriptions stream is discoverable from the manifest."""
    source = _get_source()
    stream_names = [s.name for s in source.streams(_CONFIG)]
    assert "subscriptions" in stream_names


def test_subscriptions_stream_reads_records():
    """subscriptions stream reads records from GET /subscriptions."""
    response = {
        "subscriptions": [
            _subscription_record("SB0001"),
            _subscription_record("SB0002", amount=2500, status="cancelled"),
        ],
        "meta": {"cursors": {"before": None, "after": None}, "limit": 500},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/subscriptions", json=response)
        output = _sync_subscriptions()

    emitted_ids = [r.record.data["id"] for r in output.records]
    assert emitted_ids == ["SB0001", "SB0002"]


def test_subscriptions_stream_handles_empty_response():
    """subscriptions stream emits no records when the API returns an empty list."""
    response = {
        "subscriptions": [],
        "meta": {"cursors": {"before": None, "after": None}, "limit": 500},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/subscriptions", json=response)
        output = _sync_subscriptions()

    assert output.records == []


def test_subscriptions_stream_paginates():
    """subscriptions stream follows cursor-based pagination across multiple pages."""
    page1 = {
        "subscriptions": [_subscription_record("SB0001")],
        "meta": {"cursors": {"before": None, "after": "SB0001"}, "limit": 500},
    }
    page2 = {
        "subscriptions": [_subscription_record("SB0002")],
        "meta": {"cursors": {"before": "SB0001", "after": None}, "limit": 500},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/subscriptions",
            [{"json": page1, "status_code": 200}, {"json": page2, "status_code": 200}],
        )
        output = _sync_subscriptions()

    emitted_ids = [r.record.data["id"] for r in output.records]
    assert emitted_ids == ["SB0001", "SB0002"]


@pytest.mark.parametrize(
    "field,value",
    [
        pytest.param("amount", 5000, id="amount"),
        pytest.param("app_fee", 100, id="app_fee"),
        pytest.param("currency", "EUR", id="currency"),
        pytest.param("day_of_month", 15, id="day_of_month"),
        pytest.param("interval", 3, id="interval"),
        pytest.param("interval_unit", "weekly", id="interval_unit"),
        pytest.param("name", "Premium Plan", id="name"),
        pytest.param("status", "pending_customer_approval", id="status"),
        pytest.param("start_date", "2025-01-01", id="start_date"),
        pytest.param("end_date", "2025-12-31", id="end_date"),
        pytest.param("count", 12, id="count"),
        pytest.param("month", "january", id="month"),
    ],
    ids=str,
)
def test_subscriptions_stream_preserves_field(field, value):
    """Each schema property is correctly passed through in emitted records."""
    response = {
        "subscriptions": [_subscription_record("SB0001", **{field: value})],
        "meta": {"cursors": {"before": None, "after": None}, "limit": 500},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/subscriptions", json=response)
        output = _sync_subscriptions()

    assert len(output.records) == 1
    assert output.records[0].record.data[field] == value


def test_subscriptions_uses_sandbox_url():
    """When gocardless_environment is 'sandbox', requests go to sandbox URL."""
    response = {
        "subscriptions": [_subscription_record("SB0001")],
        "meta": {"cursors": {"before": None, "after": None}, "limit": 500},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/subscriptions", json=response)
        output = _sync_subscriptions()

    assert len(output.records) == 1


def test_subscriptions_uses_live_url():
    """When gocardless_environment is 'live', requests go to the live API URL."""
    live_config = {**_CONFIG, "access_token": "live_test_token", "gocardless_environment": "live"}
    live_url = "https://api.gocardless.com"
    response = {
        "subscriptions": [_subscription_record("SB0001")],
        "meta": {"cursors": {"before": None, "after": None}, "limit": 500},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{live_url}/subscriptions", json=response)
        output = _sync_subscriptions(config=live_config)

    assert len(output.records) == 1


def test_subscriptions_sends_version_header():
    """The GoCardless-Version header is sent with the configured version."""
    response = {
        "subscriptions": [_subscription_record("SB0001")],
        "meta": {"cursors": {"before": None, "after": None}, "limit": 500},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/subscriptions", json=response)
        _sync_subscriptions()

    assert mocker.last_request.headers["GoCardless-Version"] == "2015-07-06"


def test_subscriptions_sends_start_date_filter():
    """The created_at[gte] query param is set from config start_date."""
    response = {
        "subscriptions": [],
        "meta": {"cursors": {"before": None, "after": None}, "limit": 500},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/subscriptions", json=response)
        _sync_subscriptions()

    assert "created_at%5Bgte%5D=2024-01-01T00%3A00%3A00Z" in mocker.last_request.url


def test_subscriptions_sends_bearer_auth():
    """Requests include the Bearer token from config."""
    response = {
        "subscriptions": [],
        "meta": {"cursors": {"before": None, "after": None}, "limit": 500},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/subscriptions", json=response)
        _sync_subscriptions()

    assert mocker.last_request.headers["Authorization"] == "Bearer sandbox_test_token"


def test_existing_streams_still_present():
    """Adding subscriptions does not remove existing streams."""
    source = _get_source()
    stream_names = sorted(s.name for s in source.streams(_CONFIG))
    assert stream_names == ["mandates", "payments", "payouts", "refunds", "subscriptions"]
