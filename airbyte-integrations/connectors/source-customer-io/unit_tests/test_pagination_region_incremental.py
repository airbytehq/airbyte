# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-customer-io` covering high-priority audit findings.

These tests verify the manifest changes that address airbytehq/airbyte-internal-issues#16327:

- `campaigns_actions` and `newsletters` paginate via `response.next` -> `start` query parameter
- All three streams emit only records whose `updated` cursor is at-or-after `config['start_date']`
  (client-side incremental sync)
- The `region` config field switches `url_base` between `api.customer.io` (US) and
  `api-eu.customer.io` (EU)
"""

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_BASE_CONFIG = {"app_api_key": "test-api-key"}


def _campaign(campaign_id: int, updated: int) -> dict:
    return {
        "id": campaign_id,
        "name": f"campaign-{campaign_id}",
        "type": "triggered",
        "active": True,
        "created": updated,
        "updated": updated,
        "state": "running",
        "actions": [],
        "msg_templates": [],
        "tags": [],
        "trigger_segment_ids": [],
    }


def _action(action_id: str, campaign_id: int, updated: int) -> dict:
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
    return {
        "id": newsletter_id,
        "name": f"newsletter-{newsletter_id}",
        "type": "newsletter",
        "created": updated,
        "updated": updated,
        "tags": [],
        "content_ids": [],
        "sent_at": [],
    }


def _sync(stream_name: str, config: dict):
    source = get_source(config=config)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(source, config, catalog)


def test_campaigns_actions_paginates_via_response_next_into_start_param():
    """`campaigns_actions` follows `response.next` and forwards it as the `start` query parameter."""
    campaigns_response = {"campaigns": [_campaign(1, 1700000000)]}
    actions_page_1 = {
        "actions": [_action("a-1", 1, 1700000000), _action("a-2", 1, 1700000001)],
        "next": "page-2-token",
    }
    actions_page_2 = {
        "actions": [_action("a-3", 1, 1700000002)],
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
        output = _sync("campaigns_actions", _BASE_CONFIG)

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == ["a-1", "a-2", "a-3"], (
        f"expected all 3 paginated actions to be emitted, got {emitted_ids}"
    )

    actions_requests = [r for r in mocker.request_history if r.path == "/v1/campaigns/1/actions"]
    assert len(actions_requests) == 2, (
        f"expected 2 paginated requests against /campaigns/1/actions, got {len(actions_requests)}"
    )
    assert "start" not in actions_requests[0].qs, (
        "first request must not include the `start` cursor parameter"
    )
    assert actions_requests[1].qs.get("start") == ["page-2-token"], (
        f"second request must forward the `start` cursor from `response.next`; got {actions_requests[1].qs}"
    )


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
        output = _sync("newsletters", _BASE_CONFIG)

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [1, 2, 3], f"expected all 3 paginated newsletters, got {emitted_ids}"

    newsletter_requests = [r for r in mocker.request_history if r.path == "/v1/newsletters"]
    assert len(newsletter_requests) == 2, (
        f"expected 2 paginated requests against /newsletters, got {len(newsletter_requests)}"
    )
    assert newsletter_requests[0].qs.get("limit") == ["100"], (
        f"first request must include the `limit` page-size parameter; got {newsletter_requests[0].qs}"
    )
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
        output = _sync("newsletters", config)

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [99]
    eu_requests = [r for r in mocker.request_history if r.hostname == "api-eu.customer.io"]
    us_requests = [r for r in mocker.request_history if r.hostname == "api.customer.io"]
    assert eu_requests, "expected at least one request against api-eu.customer.io for EU region"
    assert not us_requests, (
        f"expected no requests against the US host when region=EU, got {[r.url for r in us_requests]}"
    )


def test_us_region_default_uses_api_customer_io_host():
    """Default (US) configuration continues to target `api.customer.io` (no breaking change)."""
    with requests_mock.Mocker() as mocker:
        mocker.get(
            "https://api.customer.io/v1/newsletters",
            json={"newsletters": [_newsletter(1, 1700000000)], "next": None},
        )
        mocker.get("https://api-eu.customer.io/v1/newsletters", status_code=599)
        output = _sync("newsletters", _BASE_CONFIG)

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [1]
    eu_requests = [r for r in mocker.request_history if r.hostname == "api-eu.customer.io"]
    assert not eu_requests, (
        f"expected no requests against the EU host when region defaults to US, got {[r.url for r in eu_requests]}"
    )


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
        output = _sync("newsletters", config)

    emitted_ids = sorted(record.record.data["id"] for record in output.records)
    assert emitted_ids == [2, 3], (
        f"expected only records with `updated` >= start_date to be emitted, got {emitted_ids}"
    )


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
        output = _sync("campaigns", config)

    emitted_ids = sorted(record.record.data["id"] for record in output.records)
    assert emitted_ids == [11]
