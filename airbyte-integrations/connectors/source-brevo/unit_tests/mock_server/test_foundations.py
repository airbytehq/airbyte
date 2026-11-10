# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging

import pytest
from conftest import get_source
from freezegun import freeze_time
from jsonschema import Draft7Validator

from airbyte_cdk.models import AirbyteStateMessage, FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import BrevoRequestBuilder
from mock_server.response_builder import BrevoResponseBuilder


NOW = "2023-11-14T23:59:59Z"
UPDATED = "2023-11-14T23:00:00.000Z"
STATE_VALUE = "2023-11-14T23:00:00.000000Z"


def run_read(
    name: str, mode: SyncMode = SyncMode.full_refresh, state: list[AirbyteStateMessage] | None = None, expect_error: bool = False
) -> EntrypointOutput:
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(name, mode).build()
    output = read(get_source(config, state=state), config=config, catalog=catalog, state=state or [])
    assert bool(output.errors) == expect_error
    return output


def mock_page(mocker: HttpMocker, path: str, field: str | None, records: list[dict], **query: str | int) -> HttpRequest:
    request = BrevoRequestBuilder(path).with_query_params(**query).build()
    mocker.get(request, BrevoResponseBuilder(field).with_records(records).build())
    return request


def assert_calls(mocker: HttpMocker, requests: list[HttpRequest]) -> None:
    for request in requests:
        mocker.assert_number_of_calls(request, 1)


def mock_pages(mocker: HttpMocker, path: str, field: str, size: int, records: list[dict], **query: str | int) -> list[HttpRequest]:
    requests = []
    for offset, page in [(0, records[:size]), (size, records[size:]), (size * 2, [])]:
        requests.append(mock_page(mocker, path, field, page, limit=size, offset=offset, sort="asc", **query))
    return requests


@pytest.mark.parametrize(
    "name,size,field",
    [("contacts_lists_contacts", 500, "contacts"), ("emailCampaigns", 100, "campaigns"), ("smsCampaigns", 1000, "campaigns")],
)
@freeze_time(NOW)
def test_page_sizes_and_empty_page_termination(name: str, size: int, field: str) -> None:
    records = [{"id": i, "modifiedAt": UPDATED} for i in range(size * 2)]
    with HttpMocker() as mocker:
        query = {}
        path = name
        if name == "contacts_lists_contacts":
            mock_page(mocker, "contacts/lists", "lists", [{"id": 71}], limit=50, offset=0, sort="asc")
            path = "contacts/lists/71/contacts"
            query = {"modifiedSince": "2023-11-14T00:00:00Z"}
        requests = mock_pages(mocker, path, field, size, records, **query)
        output = run_read(name)
        assert [r.record.data["id"] for r in output.records] == list(range(size * 2))
        assert_calls(mocker, requests)


@pytest.mark.parametrize("name,size", [("emailCampaigns", 100), ("smsCampaigns", 1000)])
@freeze_time(NOW)
def test_campaigns_filter_modified_at_without_sent_date_parameters(name: str, size: int) -> None:
    with HttpMocker() as mocker:
        request = mock_page(mocker, name, "campaigns", [{"id": 1, "modifiedAt": UPDATED}], limit=size, offset=0, sort="asc")
        first = run_read(name, SyncMode.incremental)
        assert first.most_recent_state.stream_state.__dict__ == {"modifiedAt": STATE_VALUE}
        assert_calls(mocker, [request])
    state = [first.state_messages[-1].state]
    with HttpMocker() as mocker:
        request = mock_page(
            mocker,
            name,
            "campaigns",
            [
                {"id": 1, "modifiedAt": "2023-11-14T22:00:00.000Z"},
                {"id": 2, "modifiedAt": UPDATED},
                {"id": 3, "modifiedAt": "2023-11-14T23:30:00.000Z"},
            ],
            limit=size,
            offset=0,
            sort="asc",
        )
        output = run_read(name, SyncMode.incremental, state)
        assert [r.record.data["id"] for r in output.records] == [2, 3]
        assert output.most_recent_state.stream_state.__dict__ == {"modifiedAt": "2023-11-14T23:30:00.000000Z"}
        assert_calls(mocker, [request])


@pytest.mark.parametrize("name", ["crm_tasks", "crm_notes"])
@freeze_time(NOW)
def test_crm_accepts_seconds_state_and_sends_milliseconds(name: str) -> None:
    state = StateBuilder().with_stream_state(name, {"updatedAt": "1700000000"}).build()
    with HttpMocker() as mocker:
        request = mock_page(
            mocker,
            name.replace("_", "/"),
            "items" if name == "crm_tasks" else None,
            [{"id": "new", "updatedAt": UPDATED}],
            limit=50,
            offset=0,
            sort="asc",
            dateFrom="1700000000000",
            dateTo="1700006399000",
        )
        output = run_read(name, SyncMode.incremental, state)
        assert [r.record.data["id"] for r in output.records] == ["new"]
        assert output.most_recent_state.stream_state.__dict__ == {"updatedAt": "1700002800000"}
        assert_calls(mocker, [request])


@pytest.mark.parametrize(
    "name,parent_path,parent_field,child_field,parent_id_field",
    [
        ("contacts_folders_lists", "contacts/folders", "folders", "lists", "folderId"),
        ("contacts_lists_contacts", "contacts/lists", "lists", "contacts", "listId"),
    ],
)
@freeze_time(NOW)
def test_parent_ids_are_injected(name: str, parent_path: str, parent_field: str, child_field: str, parent_id_field: str) -> None:
    with HttpMocker() as mocker:
        requests = [mock_page(mocker, parent_path, parent_field, [{"id": 71}, {"id": 83}], limit=50, offset=0, sort="asc")]
        for parent_id in [71, 83]:
            query = {"modifiedSince": "2023-11-14T00:00:00Z"} if name == "contacts_lists_contacts" else {}
            if name == "contacts_lists_contacts":
                mock_page(
                    mocker,
                    f"{parent_path}/{parent_id}/{child_field}",
                    child_field,
                    [{"id": 9, "modifiedAt": UPDATED}],
                    limit=50,
                    offset=0,
                    sort="asc",
                    **query,
                )
            requests.append(
                mock_page(
                    mocker,
                    f"{parent_path}/{parent_id}/{child_field}",
                    child_field,
                    [{"id": 9, "modifiedAt": UPDATED}],
                    limit=500 if query else 50,
                    offset=0,
                    sort="asc",
                    **query,
                )
            )
        output = run_read(name)
        assert {(r.record.data["id"], r.record.data[parent_id_field]) for r in output.records} == {(9, 71), (9, 83)}
        config = ConfigBuilder().build()
        catalog = get_source(config).discover(logging.getLogger("brevo-test"), config)
        schema = next(s.json_schema for s in catalog.streams if s.name == name)
        for message in output.records:
            assert parent_id_field in schema["properties"]
            Draft7Validator(schema["properties"][parent_id_field]).validate(message.record.data[parent_id_field])
        assert_calls(mocker, requests)


SCHEMA_RECORDS = [
    (
        "webhooks",
        "webhooks",
        "webhooks",
        {
            "id": 1,
            "auth": {"type": "bearer", "token": "example"},
            "batched": True,
            "headers": [{"key": "x-test", "value": "yes"}],
            "domain": "example.com",
        },
        {},
    ),
    (
        "contacts",
        "contacts",
        "contacts",
        {"id": 1, "modifiedAt": UPDATED, "listUnsubscribed": [5], "whatsappBlacklisted": True, "consentGroups": ["marketing"]},
        {"limit": 1000, "offset": 0, "sort": "asc", "modifiedSince": "2023-11-14T00:00:00.000000Z"},
    ),
    (
        "contacts_lists_contacts",
        "contacts/lists/71/contacts",
        "contacts",
        {"id": 1, "modifiedAt": UPDATED, "listUnsubscribed": [5], "whatsappBlacklisted": True, "consentGroups": ["marketing"]},
        {"limit": 500, "offset": 0, "sort": "asc", "modifiedSince": "2023-11-14T00:00:00Z"},
    ),
    (
        "contacts_attributes",
        "contacts/attributes",
        "attributes",
        {"category": "normal", "name": "STATUS", "multiCategoryOptions": ["yes"], "enumeration": [{"valueStr": "yes"}]},
        {},
    ),
    ("crm_attributes_deals", "crm/attributes/deals", None, {"internalName": "stage", "isValueReadonly": True}, {}),
    ("account", "account", None, {"organization_id": "1", "user_id": 2}, {}),
    ("domains", "senders/domains", "domains", {"id": "1", "ip": "192.0.2.1"}, {}),
    ("senders", "senders", "senders", {"id": 1, "ips": [{"domain": "example.com", "ip": "192.0.2.1", "weight": 5}]}, {}),
    (
        "emailCampaigns",
        "emailCampaigns",
        "campaigns",
        {"id": 1, "modifiedAt": UPDATED, "statistics": {"campaignStats": [{"appleMppOpens": 2, "estimatedViews": 3}]}},
        {"limit": 100, "offset": 0, "sort": "asc"},
    ),
    (
        "smsCampaigns",
        "smsCampaigns",
        "campaigns",
        {"id": 1, "modifiedAt": UPDATED, "recipients": {"exclusionLists": [7]}},
        {"limit": 1000, "offset": 0, "sort": "asc"},
    ),
]


def assert_declared_values(schema: dict, record: dict) -> None:
    for key, value in record.items():
        assert key in schema["properties"], f"Emitted field {key} is undeclared"
        prop = schema["properties"][key]
        Draft7Validator(prop).validate(value)
        if isinstance(value, dict) and "properties" in prop:
            assert_declared_values(prop, value)
        if isinstance(value, list):
            if key in {"ips", "exclusionLists"}:
                assert "items" in prop
            for item in value:
                if isinstance(item, dict) and "properties" in prop.get("items", {}):
                    assert_declared_values(prop["items"], item)


@pytest.mark.parametrize("name,path,field,record,query", SCHEMA_RECORDS, ids=[r[0] for r in SCHEMA_RECORDS])
@freeze_time(NOW)
def test_added_fields_are_emitted_and_conform_to_discovery(name: str, path: str, field: str | None, record: dict, query: dict) -> None:
    with HttpMocker() as mocker:
        if name == "contacts_lists_contacts":
            mock_page(mocker, "contacts/lists", "lists", [{"id": 71}], limit=50, offset=0, sort="asc")
        if name == "account":
            response = BrevoResponseBuilder(None).with_records(record).build()
            request = BrevoRequestBuilder(path).build()
            mocker.get(request, response)
        else:
            request = mock_page(mocker, path, field, [record], **query)
            if name == "contacts_lists_contacts":
                mock_page(mocker, path, field, [record], **dict(query, limit=50))
            if name in {"emailCampaigns", "smsCampaigns"}:
                mock_page(
                    mocker,
                    path,
                    field,
                    [record],
                    **dict(
                        query,
                        limit=50 if name == "emailCampaigns" else 500,
                        startDate="2023-11-14T00:00:00.000000Z",
                        endDate="2023-11-14T23:59:59.000000Z",
                    ),
                )
        output = run_read(name)
        assert len(output.records) == 1
        emitted = output.records[0].record.data
        assert all(emitted[key] == value for key, value in record.items())
        config = ConfigBuilder().build()
        catalog = get_source(config).discover(logging.getLogger("brevo-test"), config)
        schema = next(s.json_schema for s in catalog.streams if s.name == name)
        assert_declared_values(schema, emitted)
        assert_calls(mocker, [request])


NEW_STREAMS = [
    ("inbound_email_events", "inbound/events", "events", 500, "uuid", "date"),
    ("transactional_email_events", "smtp/statistics/events", "events", 5000, "messageId", "date"),
    ("processes", "processes", "processes", 50, "id", None),
    ("products", "products", "products", 1000, "id", "modifiedAt"),
    ("categories", "categories", "categories", 100, "id", "modifiedAt"),
    ("email_templates", "smtp/templates", "templates", 1000, "id", None),
]


def event_query(name: str, start: str = "2023-11-14T00:00:00.000000Z") -> dict[str, str]:
    if name == "transactional_email_events":
        return {"startDate": "2023-11-14", "endDate": "2023-11-14"}
    if name == "inbound_email_events":
        return {"startDate": start, "endDate": "2023-11-14T23:59:59.000000Z"}
    if name in {"products", "categories"}:
        return {"modifiedSince": start}
    return {}


@pytest.mark.parametrize("name,path,field,size,id_field,cursor", NEW_STREAMS, ids=[r[0] for r in NEW_STREAMS])
@freeze_time(NOW)
def test_new_stream_reads_two_pages_and_resumes(name: str, path: str, field: str, size: int, id_field: str, cursor: str | None) -> None:
    ids = list(range(size * 2)) if name in {"processes", "email_templates"} else [str(i) for i in range(size * 2)]
    records = [{id_field: i, **({cursor: UPDATED} if cursor else {})} for i in ids]
    mode = SyncMode.incremental if cursor else SyncMode.full_refresh
    with HttpMocker() as mocker:
        requests = mock_pages(mocker, path, field, size, records, **event_query(name))
        output = run_read(name, mode)
        assert [r.record.data[id_field] for r in output.records] == ids
        assert_calls(mocker, requests)
        if cursor:
            expected = "2023-11-14" if name == "transactional_email_events" else STATE_VALUE
            assert output.most_recent_state.stream_state.__dict__ == {cursor: expected}
    if cursor:
        state = [output.state_messages[-1].state]
        with HttpMocker() as mocker:
            request = mock_page(
                mocker,
                path,
                field,
                [{id_field: "boundary", cursor: UPDATED}, {id_field: "new", cursor: "2023-11-14T23:30:00.000Z"}],
                limit=size,
                offset=0,
                sort="asc",
                **event_query(name, STATE_VALUE),
            )
            resumed = run_read(name, mode, state)
            assert [r.record.data[id_field] for r in resumed.records] == ["boundary", "new"]
            expected = "2023-11-14" if name == "transactional_email_events" else "2023-11-14T23:30:00.000000Z"
            assert resumed.most_recent_state.stream_state.__dict__ == {cursor: expected}
            assert_calls(mocker, [request])


@pytest.mark.parametrize("name,path,field,size,id_field,cursor", NEW_STREAMS, ids=[r[0] for r in NEW_STREAMS])
@pytest.mark.parametrize("unauthorized", [False, True], ids=["empty", "unauthorized"])
@freeze_time(NOW)
def test_new_stream_empty_and_error_responses(
    name: str, path: str, field: str, size: int, id_field: str, cursor: str | None, unauthorized: bool
) -> None:
    with HttpMocker() as mocker:
        request = BrevoRequestBuilder(path).with_query_params(limit=size, offset=0, sort="asc", **event_query(name)).build()
        if unauthorized:
            response = HttpResponse(body='{"code":"unauthorized","message":"Invalid API key"}', status_code=401)
        else:
            response = BrevoResponseBuilder(field).with_records([]).build()
        mocker.get(request, response)
        output = run_read(name, SyncMode.incremental if cursor else SyncMode.full_refresh, expect_error=unauthorized)
        assert output.records == []
        if unauthorized:
            assert any(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
        assert_calls(mocker, [request])
