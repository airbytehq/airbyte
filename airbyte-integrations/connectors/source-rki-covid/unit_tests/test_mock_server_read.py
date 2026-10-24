#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime, timedelta

from source_rki_covid import SourceRkiCovid

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {"start_date": "2026-09-01"}
_STREAM_NAME = "germany_history_cases"
_STATES_URL = "https://api.corona-zahlen.org/states/"


def _read(stream_name, sync_mode, config, state=None, catalog=None):
    return read(
        SourceRkiCovid(),
        config,
        catalog or CatalogBuilder().with_stream(stream_name, sync_mode).build(),
        state=state or StateBuilder().build(),
    )


def _incremental_catalog():
    return ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {
                        "name": _STREAM_NAME,
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": False,
                        "default_cursor_field": ["date"],
                    },
                    "sync_mode": "incremental",
                    "cursor_field": ["date"],
                    "destination_sync_mode": "append",
                }
            ]
        }
    )


def _start_date_and_records():
    today = datetime.now().date()
    start_date = (today - timedelta(days=10)).isoformat()
    records = [
        {"date": (today - timedelta(days=3)).isoformat(), "cases": 12},
        {"date": (today - timedelta(days=1)).isoformat(), "cases": 27},
    ]
    days = max((datetime.now() - datetime.strptime(start_date, "%Y-%m-%d")).days, 1)
    return {"start_date": start_date}, records, days


def test_germany_states_full_refresh_reads_records():
    response = {
        "data": {
            "BE": {"name": "Berlin", "cases": 100},
            "BY": {"name": "Bayern", "cases": 200},
        }
    }
    with HttpMocker() as http_mocker:
        http_mocker.get(HttpRequest(_STATES_URL), HttpResponse(json.dumps(response)))
        output = _read("germany_states", SyncMode.full_refresh, _CONFIG)

    assert output.errors == []
    assert [message.record.data for message in output.records] == [
        {"name": "Berlin", "cases": 100},
        {"name": "Bayern", "cases": 200},
    ]


def test_germany_history_cases_incremental_read_emits_latest_state():
    config, records, days = _start_date_and_records()
    request = HttpRequest(f"https://api.corona-zahlen.org/germany/history/cases/{days}")
    response = {"data": records}
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(response)))
        output = _read(_STREAM_NAME, SyncMode.incremental, config, catalog=_incremental_catalog())

    assert output.errors == []
    assert [message.record.data for message in output.records] == records
    assert output.state_messages[-1].state.stream.stream_state.date == records[-1]["date"]


def test_germany_history_cases_incremental_read_filters_existing_cursor_and_advances_state():
    config, records, days = _start_date_and_records()
    earlier_record = {"date": (datetime.now().date() - timedelta(days=5)).isoformat(), "cases": 3}
    records = [earlier_record, *records]
    cursor = records[1]["date"]
    state = StateBuilder().with_stream_state(_STREAM_NAME, {"date": cursor}).build()
    request = HttpRequest(f"https://api.corona-zahlen.org/germany/history/cases/{days}")
    response = {"data": records}
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(response)))
        output = _read(_STREAM_NAME, SyncMode.incremental, config, state=state, catalog=_incremental_catalog())

    assert output.errors == []
    assert [message.record.data for message in output.records] == [records[-1]]
    assert output.state_messages[-1].state.stream.stream_state.date == records[-1]["date"]
