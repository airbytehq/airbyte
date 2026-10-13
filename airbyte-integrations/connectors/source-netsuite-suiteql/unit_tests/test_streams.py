# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from requests_oauthlib import OAuth1
from source_netsuite_suiteql.streams import SuiteqlStream


def make_stream(page_size: int = 1000, table_name: str = "customer") -> SuiteqlStream:
    return SuiteqlStream(
        table_name=table_name,
        base_url="https://12345.suitetalk.api.netsuite.com",
        page_size=page_size,
        auth=OAuth1("key", "secret", "token", "token-secret"),
        primary_key=["id"],
        cursor_field="lastmodifieddate",
    )


def test_read_records_posts_query_and_paginates(requests_mock) -> None:
    endpoint = "https://12345.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"
    requests_mock.post(
        endpoint,
        [
            {"json": {"items": [{"id": "101"}], "count": 1, "offset": 0, "hasMore": True}},
            {"json": {"items": [{"id": "102"}], "count": 1, "offset": 1, "hasMore": False}},
        ],
    )

    records = list(make_stream(page_size=1).read_records(sync_mode=None))

    assert records == [{"id": "101"}, {"id": "102"}]
    assert [request.qs for request in requests_mock.request_history] == [
        {"limit": ["1"], "offset": ["0"]},
        {"limit": ["1"], "offset": ["1"]},
    ]
    assert requests_mock.request_history[0].json() == {
        "q": ("SELECT *, TO_CHAR(lastmodifieddate, 'YYYY-MM-DD HH24:MI:SS') AS cursor_ts " "FROM customer ORDER BY cursor_ts, id"),
    }
    assert requests_mock.request_history[0].headers["Prefer"] == b"transient"


def test_get_json_schema_infers_sampled_fields(requests_mock) -> None:
    endpoint = "https://12345.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"
    requests_mock.post(endpoint, json={"items": [{"id": "101", "active": True, "amount": 12.5}]})

    schema = make_stream().get_json_schema()

    assert schema["properties"] == {
        "id": {"type": ["null", "string"]},
        "active": {"type": ["null", "boolean"]},
        "amount": {"type": ["null", "number"]},
    }
    assert requests_mock.last_request.qs == {"limit": ["100"], "offset": ["0"]}


def test_get_json_schema_merges_types_across_sampled_records(requests_mock) -> None:
    endpoint = "https://12345.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"
    requests_mock.post(
        endpoint,
        json={"items": [{"id": "101", "lastmodifieddate": None}, {"id": "102", "lastmodifieddate": "2024-06-01T12:00:00Z"}]},
    )

    schema = make_stream().get_json_schema()

    assert schema["properties"]["lastmodifieddate"] == {"type": ["null", "string"]}


def test_get_json_schema_appends_only_undiscovered_schema_hints(requests_mock) -> None:
    endpoint = "https://12345.suitetalk.api.netsuite.com/services/rest/query/v1/suiteql"
    requests_mock.post(endpoint, json={"items": [{"id": "101", "custcol_can_percent_complete": "12"}]})

    schema = make_stream(table_name="transactionLine").get_json_schema()

    assert schema["properties"]["id"] == {"type": ["null", "string"]}
    assert schema["properties"]["custcol_can_percent_complete"] == {"type": ["null", "string"]}
    assert schema["properties"]["netamount"] == {"type": ["null", "number"]}


@pytest.mark.parametrize("table_name", ["transactionLine", "transactionline", "TRANSACTIONLINE"])
def test_schema_hint_lookup_ignores_table_name_case(table_name: str) -> None:
    hint = make_stream(table_name=table_name)._schema_hint()

    assert "custcol_ns_can_contract" in hint["properties"]


def test_incremental_stream_uses_state_for_cursor_parameter_and_deduplication() -> None:
    stream = SuiteqlStream(
        table_name="customer",
        base_url="https://12345.suitetalk.api.netsuite.com",
        page_size=1000,
        auth=OAuth1("key", "secret", "token", "token-secret"),
        primary_key=["id", "email"],
        cursor_field="lastmodifieddate",
    )

    assert stream.supports_incremental
    assert stream.primary_key == [["id"], ["email"]]
    assert stream.request_body_json(stream_state={"lastmodifieddate": "2024-02-01 00:00:00"}) == {
        "q": (
            "SELECT *, TO_CHAR(lastmodifieddate, 'YYYY-MM-DD HH24:MI:SS') AS cursor_ts FROM customer "
            "WHERE lastmodifieddate >= TO_DATE(?, 'YYYY-MM-DD HH24:MI:SS') ORDER BY cursor_ts, id, email"
        ),
        "params": ["2024-02-01 00:00:00"],
    }
    assert stream.get_updated_state({"lastmodifieddate": "2024-02-01 00:00:00"}, {"lastmodifieddate": "2024-03-01 00:00:00"}) == {
        "lastmodifieddate": "2024-03-01 00:00:00"
    }
