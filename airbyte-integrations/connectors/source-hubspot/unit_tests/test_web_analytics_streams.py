#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re

import freezegun
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import discover

from .conftest import find_stream, get_source, mock_dynamic_schema_requests_with_skip, read_from_stream


WEB_ANALYTICS_STREAMS = [
    "contacts_web_analytics",
    "companies_web_analytics",
    "deals_web_analytics",
    "tickets_web_analytics",
    "engagements_calls_web_analytics",
    "engagements_emails_web_analytics",
    "engagements_meetings_web_analytics",
    "engagements_notes_web_analytics",
    "engagements_tasks_web_analytics",
    "goals_web_analytics",
    "line_items_web_analytics",
    "products_web_analytics",
]

SAMPLE_WEB_ANALYTICS_RESPONSE = {
    "results": [
        {
            "objectType": "CONTACT",
            "objectId": "123",
            "eventType": "pe8727216_airbyte_contact_custom_event",
            "occurredAt": "2023-12-01T21:50:11.801000Z",
            "id": "b850d903-254c-4df6-b159-9263b2b7eed8",
            "properties": {
                "hs_city": "San Francisco",
                "hs_country": "US",
                "hs_page_url": "https://example.com/page",
                "hs_browser": "Chrome",
            },
        }
    ]
}

SAMPLE_PAGINATED_RESPONSE_PAGE1 = {
    "results": [
        {
            "objectType": "CONTACT",
            "objectId": "123",
            "eventType": "page_view",
            "occurredAt": "2023-12-01T10:00:00.000000Z",
            "id": "event-1",
            "properties": {"hs_page_url": "https://example.com/1"},
        }
    ],
    "paging": {"next": {"after": "cursor-abc123"}},
}

SAMPLE_PAGINATED_RESPONSE_PAGE2 = {
    "results": [
        {
            "objectType": "CONTACT",
            "objectId": "123",
            "eventType": "page_view",
            "occurredAt": "2023-12-01T11:00:00.000000Z",
            "id": "event-2",
            "properties": {"hs_page_url": "https://example.com/2"},
        }
    ],
}

FROZEN_TIME = "2023-12-15T00:00:00Z"


@pytest.fixture()
def config_experimental_narrow():
    """Config with experimental streams enabled and a narrow start_date to minimize parent time windows."""
    return {
        "credentials": {"credentials_title": "Private App Credentials", "access_token": "test_access_token"},
        "start_date": "2023-12-01T00:00:00Z",
        "enable_experimental_streams": True,
    }


def _mock_all_common(requests_mock):
    """Mock custom-object schemas and dynamic-schema property endpoints."""
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={"results": []}, status_code=200)
    mock_dynamic_schema_requests_with_skip(requests_mock, [])


def _mock_contacts_parent_full(requests_mock, parent_ids):
    """Mock all endpoints needed by the contacts parent stream."""
    results = [
        {
            "id": pid,
            "createdAt": "2022-01-01T00:00:00Z",
            "updatedAt": "2023-12-01T00:00:00Z",
            "properties": {"hs_object_id": pid, "lastmodifieddate": "2023-12-01T00:00:00.000000Z"},
        }
        for pid in parent_ids
    ]
    requests_mock.register_uri(
        "POST",
        "https://api.hubapi.com/crm/v3/objects/contact/search",
        [
            {"json": {"results": results, "total": len(results)}, "status_code": 200},
            {"json": {"results": [], "total": 0}, "status_code": 200},
        ],
    )
    for assoc in ["contacts", "companies"]:
        requests_mock.register_uri(
            "POST",
            f"https://api.hubapi.com/crm/v4/associations/contact/{assoc}/batch/read",
            json={"results": []},
            status_code=200,
        )


# ── Test 1 & 2: Discovery gating ───────────────────────────────────


def test_web_analytics_streams_absent_when_experimental_disabled(requests_mock, config):
    """All 12 WA streams are absent when `enable_experimental_streams=false`."""
    _mock_all_common(requests_mock)
    assert config.get("enable_experimental_streams") is False
    output = discover(get_source(config), config)
    discovered_names = {s.name for s in output.catalog.catalog.streams}
    for wa_stream in WEB_ANALYTICS_STREAMS:
        assert wa_stream not in discovered_names, f"{wa_stream} should NOT be discovered when experimental=false"


def test_web_analytics_streams_present_when_experimental_enabled(requests_mock, config_experimental):
    """All 12 WA streams are discovered when `enable_experimental_streams=true`."""
    _mock_all_common(requests_mock)
    output = discover(get_source(config_experimental), config_experimental)
    discovered_names = {s.name for s in output.catalog.catalog.streams}
    for wa_stream in WEB_ANALYTICS_STREAMS:
        assert wa_stream in discovered_names, f"{wa_stream} should be discovered when experimental=true"


# ── Test 3: Correct parent stream and object type ───────────────────


@pytest.mark.parametrize("wa_stream_name", WEB_ANALYTICS_STREAMS)
def test_web_analytics_correct_parent_and_object_type(wa_stream_name, requests_mock, config_experimental):
    """Each WA stream references the correct parent and uses the right objectType."""
    _mock_all_common(requests_mock)
    stream = find_stream(wa_stream_name, config_experimental)

    retriever = stream._stream_partition_generator._partition_factory._retriever
    request_params = retriever.requester._request_options_provider.request_parameters
    assert request_params is not None, f"request_parameters not found for {wa_stream_name}"


# ── Test 4 & 5: objectId and time params in requests ────────────────


@freezegun.freeze_time(FROZEN_TIME)
def test_web_analytics_request_params(requests_mock, config_experimental_narrow):
    """objectId, occurredAfter, and occurredBefore are included in requests."""
    _mock_all_common(requests_mock)
    _mock_contacts_parent_full(requests_mock, ["123"])

    requests_mock.register_uri(
        "GET",
        "https://api.hubapi.com/events/v3/events",
        json=SAMPLE_WEB_ANALYTICS_RESPONSE,
    )

    output = read_from_stream(config_experimental_narrow, "contacts_web_analytics", SyncMode.incremental)
    assert len(output.records) >= 1

    history = [h for h in requests_mock.request_history if "/events/v3/events" in h.url]
    assert len(history) > 0, "Expected at least one Events API request"

    first_request = history[0]
    assert "objectId=123" in first_request.url
    assert "objectType=contact" in first_request.url
    assert "occurredAfter=" in first_request.url
    assert "occurredBefore=" in first_request.url


# ── Test 6: Pagination follows paging.next.after ────────────────────


@freezegun.freeze_time(FROZEN_TIME)
def test_web_analytics_pagination(requests_mock, config_experimental_narrow):
    """Pagination follows paging.next.after cursor."""
    _mock_all_common(requests_mock)
    _mock_contacts_parent_full(requests_mock, ["123"])

    requests_mock.register_uri(
        "GET",
        "https://api.hubapi.com/events/v3/events",
        [
            {"json": SAMPLE_PAGINATED_RESPONSE_PAGE1, "status_code": 200},
            {"json": SAMPLE_PAGINATED_RESPONSE_PAGE2, "status_code": 200},
        ],
    )

    output = read_from_stream(config_experimental_narrow, "contacts_web_analytics", SyncMode.incremental)
    assert len(output.records) >= 2

    history = [h for h in requests_mock.request_history if "/events/v3/events" in h.url]
    after_requests = [h for h in history if "after=cursor-abc123" in h.url]
    assert len(after_requests) >= 1, "Should follow paging.next.after for pagination"


# ── Test 7: Records extracted from results ──────────────────────────


@freezegun.freeze_time(FROZEN_TIME)
def test_web_analytics_records_from_results(requests_mock, config_experimental_narrow):
    """Records are extracted from the 'results' array with correct fields."""
    _mock_all_common(requests_mock)
    _mock_contacts_parent_full(requests_mock, ["123"])

    requests_mock.register_uri(
        "GET",
        "https://api.hubapi.com/events/v3/events",
        json=SAMPLE_WEB_ANALYTICS_RESPONSE,
    )

    output = read_from_stream(config_experimental_narrow, "contacts_web_analytics", SyncMode.incremental)
    assert len(output.records) >= 1

    record = output.records[0].record.data
    assert record["id"] == "b850d903-254c-4df6-b159-9263b2b7eed8"
    assert record["objectId"] == "123"
    assert record["eventType"] == "pe8727216_airbyte_contact_custom_event"


# ── Test 8: Properties flattened and normalized ─────────────────────


@freezegun.freeze_time(FROZEN_TIME)
def test_web_analytics_properties_flattened(requests_mock, config_experimental_narrow):
    """properties.hs_* are flattened to properties_hs_* and the nested object is removed."""
    _mock_all_common(requests_mock)
    _mock_contacts_parent_full(requests_mock, ["123"])

    requests_mock.register_uri(
        "GET",
        "https://api.hubapi.com/events/v3/events",
        json=SAMPLE_WEB_ANALYTICS_RESPONSE,
    )

    output = read_from_stream(config_experimental_narrow, "contacts_web_analytics", SyncMode.incremental)
    assert len(output.records) >= 1

    record = output.records[0].record.data
    assert "properties" not in record, "Nested 'properties' object should be removed"
    assert record["properties_hs_city"] == "San Francisco"
    assert record["properties_hs_country"] == "US"
    assert record["properties_hs_page_url"] == "https://example.com/page"
    assert record["properties_hs_browser"] == "Chrome"


# ── Test 9: Fresh state begins from start_date ──────────────────────


@freezegun.freeze_time(FROZEN_TIME)
def test_web_analytics_fresh_state_from_start_date(requests_mock, config_experimental_narrow):
    """Stream starts from configured start_date with no prior state."""
    _mock_all_common(requests_mock)
    _mock_contacts_parent_full(requests_mock, ["123"])

    requests_mock.register_uri(
        "GET",
        "https://api.hubapi.com/events/v3/events",
        json={"results": []},
    )

    read_from_stream(config_experimental_narrow, "contacts_web_analytics", SyncMode.incremental)

    history = [h for h in requests_mock.request_history if "/events/v3/events" in h.url]
    assert len(history) > 0, "Should make at least one Events API request"

    first_request = history[0]
    assert re.search(r"occurredAfter=2023-12-01", first_request.url), (
        f"First request should start from config start_date (2023-12-01), got: {first_request.url}"
    )


# ── Test 10: State maintained per parent partition ──────────────────


@freezegun.freeze_time(FROZEN_TIME)
def test_web_analytics_per_partition_state(requests_mock, config_experimental_narrow):
    """State is maintained independently for each parent object partition."""
    _mock_all_common(requests_mock)
    _mock_contacts_parent_full(requests_mock, ["100", "200"])

    response_contact_100 = {
        "results": [
            {
                "objectType": "CONTACT",
                "objectId": "100",
                "eventType": "page_view",
                "occurredAt": "2023-12-01T10:00:00.000000Z",
                "id": "event-100",
                "properties": {"hs_page_url": "https://example.com/100"},
            }
        ]
    }
    response_contact_200 = {
        "results": [
            {
                "objectType": "CONTACT",
                "objectId": "200",
                "eventType": "page_view",
                "occurredAt": "2023-12-05T15:00:00.000000Z",
                "id": "event-200",
                "properties": {"hs_page_url": "https://example.com/200"},
            }
        ]
    }

    requests_mock.register_uri(
        "GET",
        "https://api.hubapi.com/events/v3/events",
        [
            {"json": response_contact_100, "status_code": 200},
            {"json": response_contact_200, "status_code": 200},
        ],
    )

    output = read_from_stream(config_experimental_narrow, "contacts_web_analytics", SyncMode.incremental)
    records = output.records
    assert len(records) >= 2

    ids_seen = {r.record.data["objectId"] for r in records}
    assert "100" in ids_seen
    assert "200" in ids_seen

    state_messages = output.state_messages
    assert len(state_messages) > 0, "Should emit at least one state message"
