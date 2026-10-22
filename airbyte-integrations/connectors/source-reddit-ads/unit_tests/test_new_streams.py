# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from conftest import base_config, get_source
from freezegun import freeze_time
from test_campaign_report import _mock_token

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_PLACEHOLDER_ID = "a2_abc123"
_AD_ACCOUNT_URL = f"https://ads-api.reddit.com/api/v3/ad_accounts/{_PLACEHOLDER_ID}"
_AD_GROUP_URL = f"{_AD_ACCOUNT_URL}/ad_groups"
# Report metrics that Reddit's v3 OpenAPI spec types as int64.
_INTEGER_REPORT_METRICS = {
    "clicks",
    "conversion_lead_clicks",
    "conversion_lead_total_value",
    "conversion_lead_views",
    "conversion_page_visit_clicks",
    "conversion_page_visit_views",
    "conversion_purchase_clicks",
    "conversion_purchase_total_items",
    "conversion_purchase_total_value",
    "conversion_purchase_views",
    "conversion_search_clicks",
    "conversion_search_views",
    "conversion_sign_up_clicks",
    "conversion_sign_up_views",
    "conversion_signup_total_value",
    "conversion_view_content_clicks",
    "conversion_view_content_views",
    "engaged_click",
    "impressions",
    "key_conversion_clicks",
    "key_conversion_total_count",
    "key_conversion_views",
    "reach",
    "reddit_leads",
    "spend",
    "video_viewable_impressions",
}


def _catalog(stream_name: str, sync_mode: SyncMode = SyncMode.incremental):
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def _read_ad_groups(config: dict, rows: list[dict], state=None) -> tuple[list[str], object]:
    catalog = _catalog("ad_group")
    with freeze_time("2026-10-17T00:00:00Z"), HttpMocker() as http_mocker:
        http_mocker.get(HttpRequest(_AD_GROUP_URL), HttpResponse(body=json.dumps({"data": rows}), status_code=200))
        _mock_token(http_mocker)
        output = read(get_source(config, catalog, state), config, catalog, state=state)

    assert output.errors == []
    return [message.record.data["id"] for message in output.records], output.state_messages[-1].state


def test_ad_account_reads_one_record_with_id() -> None:
    config = base_config()
    catalog = _catalog("ad_account", SyncMode.full_refresh)
    request = HttpRequest(_AD_ACCOUNT_URL, headers={"Authorization": "Bearer test-access-token"})

    with HttpMocker() as http_mocker:
        http_mocker.get(
            request,
            HttpResponse(body=json.dumps({"data": {"id": _PLACEHOLDER_ID}}), status_code=200),
        )
        token_request = _mock_token(http_mocker)
        output = read(get_source(config, catalog), config, catalog)

    assert output.errors == []
    assert len(output.records) == 1
    assert output.records[0].record.data["id"] == _PLACEHOLDER_ID
    http_mocker.assert_number_of_calls(token_request, 1)
    http_mocker.assert_number_of_calls(request, 1)


def test_ad_group_paginates_and_filters_modified_at_client_side() -> None:
    config = base_config(start_time="2026-09-26T00:00:00Z")
    catalog = _catalog("ad_group")
    first_request = HttpRequest(_AD_GROUP_URL)
    next_request = HttpRequest(_AD_GROUP_URL, query_params={"page.token": "cursor="})
    first_page = {
        "data": [
            {"id": "a2_abc123", "name": "before-start", "modified_at": "2026-09-25T00:00:00Z"},
            {"id": "a2_def456", "name": "kept-first", "modified_at": "2026-09-27T00:00:00Z"},
        ],
        "pagination": {"next_url": f"{_AD_GROUP_URL}?page.token=cursor%3D"},
    }
    second_page = {"data": [{"id": "a2_ghi789", "name": "kept-second", "modified_at": "2026-09-28T00:00:00Z"}]}

    with freeze_time("2026-10-17T00:00:00Z"), HttpMocker() as http_mocker:
        http_mocker.get(first_request, HttpResponse(body=json.dumps(first_page), status_code=200))
        http_mocker.get(next_request, HttpResponse(body=json.dumps(second_page), status_code=200))
        _mock_token(http_mocker)
        output = read(get_source(config, catalog), config, catalog)

    assert output.errors == []
    assert {message.record.data["name"] for message in output.records} == {"kept-first", "kept-second"}
    http_mocker.assert_number_of_calls(first_request, 1)
    http_mocker.assert_number_of_calls(next_request, 1)


def test_ad_group_second_sync_from_emitted_state_skips_rows_before_state() -> None:
    config = base_config(start_time="2026-09-26T00:00:00Z")
    rows = [
        {"id": "before-start", "modified_at": "2026-09-25T13:13:56.104000+00:00"},
        {"id": "older", "modified_at": "2026-09-27T13:13:56.104000+00:00"},
        {"id": "newest", "modified_at": "2026-09-28T13:13:56.104000+00:00"},
    ]
    ids, state = _read_ad_groups(config, rows)
    assert ids == ["older", "newest"]
    assert state.stream.stream_state.modified_at == "2026-09-28T13:13:56+0000"

    rows.append({"id": "new", "modified_at": "2026-09-29T08:00:00.000000+00:00"})
    ids, state = _read_ad_groups(config, rows, state=[state])
    assert ids == ["newest", "new"]
    assert state.stream.stream_state.modified_at == "2026-09-29T08:00:00+0000"


def test_discover_pins_new_stream_keys_formats_and_report_columns() -> None:
    config = base_config()
    streams = {stream.name: stream for stream in discover(get_source(config), config).catalog.catalog.streams}
    properties = {name: stream.json_schema["properties"] for name, stream in streams.items()}
    new_reports = ["ad_account_report", "ad_group_report", "ad_report"]

    assert {name: streams[name].source_defined_primary_key for name in ["ad_account", "ad_group", *new_reports]} == {
        "ad_account": [["id"]],
        "ad_group": [["id"]],
        "ad_account_report": [["account_id"], ["date"]],
        "ad_group_report": [["ad_group_id"], ["date"]],
        "ad_report": [["ad_id"], ["date"]],
    }
    for name in new_reports:
        assert {"impressions", "spend"} <= properties[name].keys()
        assert properties[name]["date"] == {"type": "string", "format": "date"}
    assert properties["campaign_report"]["date"] == {"type": "string", "format": "date"}
    date_time_fields = {
        "ad": {"created_at", "modified_at", "preview_expiry"},
        "ad_account": {"created_at", "modified_at"},
        "ad_group": {"created_at", "modified_at", "start_time", "end_time"},
        "campaign": {"created_at", "modified_at", "start_time", "end_time"},
    }
    for name, fields in date_time_fields.items():
        assert {field for field, schema in properties[name].items() if schema.get("format") == "date-time"} == fields
    assert [name for name in ["campaign_report", *new_reports] if "campaign_id" in properties[name]] == [
        "campaign_report",
        "ad_group_report",
        "ad_report",
    ]


def test_discover_types_report_counts_and_spend_cap_as_integers() -> None:
    config = base_config()
    streams = {stream.name: stream for stream in discover(get_source(config), config).catalog.catalog.streams}
    properties = {name: stream.json_schema["properties"] for name, stream in streams.items()}

    for name in ["campaign_report", "ad_account_report", "ad_group_report", "ad_report"]:
        metric_types = {field: schema.get("type") for field, schema in properties[name].items()}
        assert {field for field, field_type in metric_types.items() if field_type == ["integer", "null"]} == _INTEGER_REPORT_METRICS
        for field in ["cpc", "ctr", "ecpm", "frequency", "conversion_roas", "conversion_purchase_total_value_all"]:
            assert metric_types[field] == ["number", "null"]
    assert properties["campaign"]["spend_cap"] == {"type": ["integer", "null"]}
