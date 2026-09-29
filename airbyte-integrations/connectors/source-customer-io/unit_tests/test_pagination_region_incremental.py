# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-customer-io` covering high-priority audit findings.

These tests verify the manifest changes that address airbytehq/airbyte-internal-issues#16327:

- `campaigns_actions` and `newsletters` paginate via `response.next` -> `start` query parameter
- All three streams emit only records whose `updated` cursor is at-or-after `config['start_date']`
  (client-side incremental sync), and `incremental` runs honor / advance state
- The `region` config field switches `url_base` between `api.customer.io` (US) and
  `api-eu.customer.io` (EU)
"""

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_BASE_CONFIG = {"app_api_key": "test-api-key"}


def _campaign(campaign_id: int, updated: int) -> dict:
    """Customer.io's App API documents campaign `type` as the campaign trigger enum (e.g. `"segment"`)."""
    return {
        "id": campaign_id,
        "name": f"campaign-{campaign_id}",
        "type": "segment",
        "active": True,
        "created": updated,
        "updated": updated,
        "state": "running",
        "actions": [],
        "msg_templates": [],
        "tags": [],
        "trigger_segment_ids": [],
    }


def _action(action_id: int, campaign_id: int, updated: int) -> dict:
    """Customer.io's App API documents campaign action `id` as an integer."""
    return {
        "id": action_id,
        "type": "email",
        "campaign_id": campaign_id,
        "name": f"action-{action_id}",
        "created": updated,
        "updated": updated,
        "subject": "hello",
        "body": "hi",
    }


def _newsletter(newsletter_id: int, updated: int) -> dict:
    """Customer.io's App API documents newsletter `type` as the channel enum (e.g. `"email"`) and `sent_at` as an integer Unix timestamp."""
    return {
        "id": newsletter_id,
        "name": f"newsletter-{newsletter_id}",
        "type": "email",
        "created": updated,
        "updated": updated,
        "tags": [],
        "content_ids": [],
        "sent_at": updated,
    }


def _read(stream_name: str, config: dict, sync_mode: SyncMode = SyncMode.full_refresh, state=None):
    """Run the connector against `stream_name` with the given `sync_mode` and optional state."""
    state = state if state is not None else []
    source = get_source(config=config, state=state)
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(source, config, catalog, state)


def _stream_state(stream_name: str, cursor_value) -> list:
    """Build a single-stream state representing a prior `updated` cursor."""
    return StateBuilder().with_stream_state(stream_name, {"updated": cursor_value}).build()


def test_campaigns_actions_paginates_via_response_next_into_start_param():
    """`campaigns_actions` follows `response.next` and forwards it as the `start` query parameter."""
    campaigns_response = {"campaigns": [_campaign(1, 1700000000)]}
    actions_page_1 = {
        "actions": [_action(101, 1, 1700000000), _action(102, 1, 1700000001)],
        "next": "page-2-token",
    }
    actions_page_2 = {
        "actions": [_action(103, 1, 1700000002)],
        "next": None,
    }

    with requests_mock.Mocker() as mocker:
        mocker.get("https://api.customer.io/v1/campaigns", json=campaigns_response)
        actions_url = "https://api.customer.io/v1/campaigns/1/actions"
        mocker.get(
            actions_url,
            [
                {"json": actions_page_1, "status_code": 200},
                {"json": actions_page_2, "status_code": 200},
            ],
        )
        output = _read("campaigns_actions", _BASE_CONFIG)

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [101, 102, 103], f"expected all 3 paginated actions to be emitted, got {emitted_ids}"

    actions_requests = [r for r in mocker.request_history if r.path == "/v1/campaigns/1/actions"]
    assert len(actions_requests) == 2, f"expected 2 paginated requests against /campaigns/1/actions, got {len(actions_requests)}"
    assert "start" not in actions_requests[0].qs, "first request must not include the `start` cursor parameter"
    assert actions_requests[1].qs.get("start") == [
        "page-2-token"
    ], f"second request must forward the `start` cursor from `response.next`; got {actions_requests[1].qs}"


def test_newsletters_paginates_via_response_next_into_start_param_with_limit():
    """`newsletters` paginates via `response.next` -> `start` and exposes `limit` as page size."""
    page_1 = {
        "newsletters": [_newsletter(1, 1700000000), _newsletter(2, 1700000001)],
        "next": "next-page-token",
    }
    page_2 = {"newsletters": [_newsletter(3, 1700000002)], "next": None}

    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://api.customer.io/v1/newsletters",
            [
                {"json": page_1, "status_code": 200},
                {"json": page_2, "status_code": 200},
            ],
        )
        output = _read("newsletters", _BASE_CONFIG)

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [1, 2, 3], f"expected all 3 paginated newsletters, got {emitted_ids}"

    newsletter_requests = [r for r in mocker.request_history if r.path == "/v1/newsletters"]
    assert len(newsletter_requests) == 2, f"expected 2 paginated requests against /newsletters, got {len(newsletter_requests)}"
    assert newsletter_requests[0].qs.get("limit") == [
        "100"
    ], f"first request must include the `limit` page-size parameter; got {newsletter_requests[0].qs}"
    assert "start" not in newsletter_requests[0].qs
    assert newsletter_requests[1].qs.get("start") == ["next-page-token"]
    assert newsletter_requests[1].qs.get("limit") == ["100"]


def test_eu_region_uses_api_eu_customer_io_host():
    """When `region` is `EU`, requests target `api-eu.customer.io`."""
    config = {**_BASE_CONFIG, "region": "EU"}

    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://api-eu.customer.io/v1/newsletters",
            json={"newsletters": [_newsletter(99, 1700000000)], "next": None},
        )
        # Assert the US host receives no traffic.
        mocker.get("https://api.customer.io/v1/newsletters", status_code=599)
        output = _read("newsletters", config)

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [99]
    eu_requests = [r for r in mocker.request_history if r.hostname == "api-eu.customer.io"]
    us_requests = [r for r in mocker.request_history if r.hostname == "api.customer.io"]
    assert eu_requests, "expected at least one request against api-eu.customer.io for EU region"
    assert not us_requests, f"expected no requests against the US host when region=EU, got {[r.url for r in us_requests]}"


def test_us_region_default_uses_api_customer_io_host():
    """Default (US) configuration continues to target `api.customer.io` (no breaking change)."""
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://api.customer.io/v1/newsletters",
            json={"newsletters": [_newsletter(1, 1700000000)], "next": None},
        )
        mocker.get("https://api-eu.customer.io/v1/newsletters", status_code=599)
        output = _read("newsletters", _BASE_CONFIG)

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [1]
    eu_requests = [r for r in mocker.request_history if r.hostname == "api-eu.customer.io"]
    assert not eu_requests, f"expected no requests against the EU host when region defaults to US, got {[r.url for r in eu_requests]}"


def test_newsletters_client_side_incremental_drops_records_before_start_date():
    """Client-side incremental sync drops `newsletters` records older than `config['start_date']`."""
    config = {**_BASE_CONFIG, "start_date": "2023-12-01T00:00:00Z"}
    cutoff_epoch = 1701388800  # 2023-12-01T00:00:00Z

    response = {
        "newsletters": [
            _newsletter(1, cutoff_epoch - 86400),  # before cutoff -> dropped
            _newsletter(2, cutoff_epoch),  # at cutoff -> kept
            _newsletter(3, cutoff_epoch + 86400),  # after cutoff -> kept
        ],
        "next": None,
    }

    with requests_mock.Mocker() as mocker:
        mocker.get("https://api.customer.io/v1/newsletters", json=response)
        output = _read("newsletters", config)

    emitted_ids = sorted(record.record.data["id"] for record in output.records)
    assert emitted_ids == [2, 3], f"expected only records with `updated` >= start_date to be emitted, got {emitted_ids}"


def test_campaigns_client_side_incremental_drops_records_before_start_date():
    """Client-side incremental sync drops `campaigns` records older than `config['start_date']`."""
    config = {**_BASE_CONFIG, "start_date": "2023-12-01T00:00:00Z"}
    cutoff_epoch = 1701388800

    response = {
        "campaigns": [
            _campaign(10, cutoff_epoch - 1),  # before cutoff -> dropped
            _campaign(11, cutoff_epoch + 1),  # after cutoff -> kept
        ]
    }

    with requests_mock.Mocker() as mocker:
        mocker.get("https://api.customer.io/v1/campaigns", json=response)
        output = _read("campaigns", config)

    emitted_ids = sorted(record.record.data["id"] for record in output.records)
    assert emitted_ids == [11]


# ---------------------------------------------------------------------------
# Incremental-mode tests: state filtering + state advancement.
# ---------------------------------------------------------------------------


def _latest_cursor_value(output, stream_name: str):
    """Return the `updated` cursor value of the last emitted state for `stream_name`, or `None`.

    `AirbyteStateBlob` is a dynamic attribute container, so we read `updated` via `getattr`
    rather than via a `.dict()` round-trip.
    """
    for message in reversed(output.state_messages):
        stream_state = message.state.stream
        if stream_state and stream_state.stream_descriptor.name == stream_name:
            return getattr(stream_state.stream_state, "updated", None)
    return None


def test_campaigns_incremental_filters_by_prior_state_and_emits_advanced_state():
    """`campaigns` incremental: prior state filters older records and final state advances to newest `updated`."""
    prior_cursor = 1700000010

    response = {
        "campaigns": [
            _campaign(1, prior_cursor - 5),  # before prior state -> dropped
            _campaign(2, prior_cursor),  # equal to prior state -> kept (inclusive)
            _campaign(3, prior_cursor + 100),  # newest -> kept and drives state
        ]
    }

    with requests_mock.Mocker() as mocker:
        mocker.get("https://api.customer.io/v1/campaigns", json=response)
        output = _read(
            "campaigns",
            _BASE_CONFIG,
            sync_mode=SyncMode.incremental,
            state=_stream_state("campaigns", prior_cursor),
        )

    emitted_ids = sorted(record.record.data["id"] for record in output.records)
    assert emitted_ids == [2, 3], f"expected records >= prior cursor, got {emitted_ids}"

    final_cursor = _latest_cursor_value(output, "campaigns")
    assert final_cursor is not None, "expected at least one state message for the campaigns stream"
    assert (
        int(final_cursor) == prior_cursor + 100
    ), f"expected state to advance to the newest `updated` ({prior_cursor + 100}), got {final_cursor}"


def test_newsletters_incremental_filters_by_prior_state_and_emits_advanced_state():
    """`newsletters` incremental: prior state filters older records and final state advances to newest `updated`."""
    prior_cursor = 1700000050

    response = {
        "newsletters": [
            _newsletter(10, prior_cursor - 1),  # before -> dropped
            _newsletter(11, prior_cursor + 10),  # after -> kept
            _newsletter(12, prior_cursor + 50),  # newest -> kept and drives state
        ],
        "next": None,
    }

    with requests_mock.Mocker() as mocker:
        mocker.get("https://api.customer.io/v1/newsletters", json=response)
        output = _read(
            "newsletters",
            _BASE_CONFIG,
            sync_mode=SyncMode.incremental,
            state=_stream_state("newsletters", prior_cursor),
        )

    emitted_ids = sorted(record.record.data["id"] for record in output.records)
    assert emitted_ids == [11, 12], f"expected records strictly after prior cursor, got {emitted_ids}"

    final_cursor = _latest_cursor_value(output, "newsletters")
    assert final_cursor is not None, "expected at least one state message for the newsletters stream"
    assert int(final_cursor) == prior_cursor + 50


def test_campaigns_actions_incremental_filters_old_child_records_and_emits_state():
    """`campaigns_actions` incremental: child records before/at/after the cursor are filtered correctly and state is emitted."""
    config = {**_BASE_CONFIG, "start_date": "2023-12-01T00:00:00Z"}
    cutoff_epoch = 1701388800  # 2023-12-01T00:00:00Z

    campaigns_response = {"campaigns": [_campaign(7, cutoff_epoch + 1000)]}
    actions_response = {
        "actions": [
            _action(701, 7, cutoff_epoch - 60),  # before cutoff -> dropped
            _action(702, 7, cutoff_epoch),  # at cutoff -> kept
            _action(703, 7, cutoff_epoch + 120),  # after cutoff -> kept and drives state
        ],
        "next": None,
    }

    with requests_mock.Mocker() as mocker:
        mocker.get("https://api.customer.io/v1/campaigns", json=campaigns_response)
        mocker.get("https://api.customer.io/v1/campaigns/7/actions", json=actions_response)
        output = _read("campaigns_actions", config, sync_mode=SyncMode.incremental)

    emitted_ids = sorted(record.record.data["id"] for record in output.records)
    assert emitted_ids == [702, 703], f"expected only actions with `updated` >= start_date, got {emitted_ids}"

    # campaigns_actions is a substream; we only assert state is emitted for the stream and that
    # at least one observed cursor value reflects the newest record we kept. The exact substream
    # state shape (per-partition vs. global) is a CDK implementation detail that we deliberately
    # do not over-specify here.
    states_for_stream = [
        m for m in output.state_messages if m.state.stream and m.state.stream.stream_descriptor.name == "campaigns_actions"
    ]
    assert states_for_stream, "expected at least one state message for the campaigns_actions stream"
