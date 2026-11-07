# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import freezegun
import pendulum
import pytest
import requests_mock
from jsonschema import Draft7Validator, FormatChecker

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import discover

from ..conftest import get_source
from .config import MARKETPLACE_ID, ConfigBuilder
from .test_fba_inbound_shipments import _SHIPMENT_STATUS_LIST
from .utils import read_output


BASE_URL = "https://sellingpartnerapi-na.amazon.com/fba/inbound/v0/shipments"
STREAMS = ("FbaInboundShipments", "FbaInboundShipmentItems")


def mock_inbound(mocker: requests_mock.Mocker, shipment_ids: list[str], empty: bool = False) -> list[dict]:
    queries = []
    mocker.post("https://api.amazon.com/auth/o2/token", json={"access_token": "test_token", "expires_in": 3600})

    def shipments(request, context):
        queries.append(request.qs)
        page = int(request.qs.get("nexttoken", ["0"])[0])
        payload = {"ShipmentData": [] if empty else [{"ShipmentId": shipment_ids[page]}]}
        if not empty and page + 1 < len(shipment_ids):
            payload["NextToken"] = str(page + 1)
        return {"payload": payload}

    mocker.get(BASE_URL, json=shipments)
    for shipment_id in shipment_ids:
        mocker.get(f"{BASE_URL}/{shipment_id}/items", json={"payload": {"ItemData": [{"SellerSKU": f"SKU-{shipment_id}"}]}})
    return queries


def expected_queries(start: str, end: str, pages: int = 1) -> list[dict]:
    common = {"marketplaceid": [MARKETPLACE_ID.lower()], "shipmentstatuslist": [_SHIPMENT_STATUS_LIST.lower()]}
    return [
        {**common, "querytype": ["date_range"], "lastupdatedafter": [start.lower()], "lastupdatedbefore": [end.lower()]},
        *[{**common, "querytype": ["next_token"], "nexttoken": [str(page)]} for page in range(1, pages)],
    ]


@pytest.mark.parametrize("stream_name", STREAMS)
@pytest.mark.parametrize("mode", ["rolling_days", "fixed"])
def test_inbound_state_handoff_and_schema(stream_name: str, mode: str) -> None:
    config = ConfigBuilder().with_inbound_rolling_days(7)
    if mode == "fixed":
        config.with_inbound_fixed_window(pendulum.datetime(2024, 5, 25))
    with requests_mock.Mocker() as mocker:
        queries = mock_inbound(mocker, ["FBA-1", "FBA-2"])
        with freezegun.freeze_time("2024-06-01T00:00:00Z"):
            first = read_output(config, stream_name, SyncMode.incremental)
            catalog = discover(get_source(config.build()), config.build()).catalog.catalog
        assert [record.record.data["ShipmentId"] for record in first.records] == ["FBA-1", "FBA-2"]
        assert queries == expected_queries("2024-05-25T00:00:00Z", "2024-06-01T00:00:00Z", pages=2)
        assert {record.record.data["LastUpdatedBefore"] for record in first.records} == {"2024-06-01T00:00:00Z"}
        schema = next(stream.json_schema for stream in catalog.streams if stream.name == stream_name)
        assert "LastUpdatedBefore" in schema["properties"]
        for record in first.records:
            Draft7Validator(schema, format_checker=FormatChecker()).validate(record.record.data)
        first_state = first.most_recent_state.stream_state.__dict__
        if stream_name == "FbaInboundShipments":
            assert first_state == {"LastUpdatedBefore": "2024-06-01T00:00:00Z"}
        else:
            assert first_state["parent_state"] == {"FbaInboundShipments": {"LastUpdatedBefore": "2024-06-01T00:00:00Z"}}
        queries.clear()
        mock_inbound(mocker, ["FBA-2", "FBA-3"])
        with freezegun.freeze_time("2024-06-03T00:00:00Z"):
            second = read_output(config, stream_name, SyncMode.incremental, state=[first.state_messages[-1].state])
        assert [record.record.data["ShipmentId"] for record in second.records] == ["FBA-2", "FBA-3"]
        # The previous upper bound is reused: changes exactly at the boundary are never skipped.
        assert {record.record.data["LastUpdatedBefore"] for record in second.records} == {"2024-06-03T00:00:00Z"}
        assert [request.qs for request in mocker.request_history if request.url.startswith(BASE_URL) and "/items" not in request.url][
            -2:
        ] == expected_queries("2024-06-01T00:00:00Z", "2024-06-03T00:00:00Z", pages=2)
        second_state = second.most_recent_state.stream_state.__dict__
        if stream_name == "FbaInboundShipments":
            assert second_state == {"LastUpdatedBefore": "2024-06-03T00:00:00Z"}
        else:
            assert second_state["parent_state"] == {"FbaInboundShipments": {"LastUpdatedBefore": "2024-06-03T00:00:00Z"}}


@pytest.mark.parametrize("stream_name", STREAMS)
@pytest.mark.parametrize("sync_mode", [SyncMode.incremental, SyncMode.full_refresh])
@freezegun.freeze_time("2024-06-01T00:00:00Z")
def test_fixed_window_and_empty_parent(stream_name: str, sync_mode: SyncMode) -> None:
    config = ConfigBuilder().with_inbound_fixed_window(pendulum.datetime(2024, 5, 10), pendulum.datetime(2024, 5, 20))
    with requests_mock.Mocker() as mocker:
        queries = mock_inbound(mocker, [], empty=True)
        output = read_output(config, stream_name, sync_mode)
        assert queries == expected_queries("2024-05-10T00:00:00Z", "2024-05-20T00:00:00Z")
        assert output.records == []
        assert not any("/items" in request.url for request in mocker.request_history)
        if sync_mode == SyncMode.incremental:
            state = output.most_recent_state.stream_state.__dict__
            if stream_name == "FbaInboundShipments":
                assert state == {"LastUpdatedBefore": "2024-05-10T00:00:00Z"}
            else:
                assert state["parent_state"] == {"FbaInboundShipments": {"LastUpdatedBefore": "2024-05-10T00:00:00Z"}}


@pytest.mark.parametrize("stream_name", STREAMS)
def test_future_fixed_end_does_not_skip_updates(stream_name: str) -> None:
    config = ConfigBuilder().with_inbound_fixed_window(pendulum.datetime(2024, 5, 25), pendulum.datetime(2024, 6, 10))
    with requests_mock.Mocker() as mocker:
        queries = mock_inbound(mocker, ["FBA-1"])
        with freezegun.freeze_time("2024-06-01T00:00:00Z"):
            first = read_output(config, stream_name, SyncMode.incremental)
        assert queries == expected_queries("2024-05-25T00:00:00Z", "2024-06-01T00:00:00Z")
        first_state = first.most_recent_state.stream_state.__dict__
        assert parent_shipment_checkpoint(stream_name, first_state) == {"LastUpdatedBefore": "2024-06-01T00:00:00Z"}
        queries = mock_inbound(mocker, ["FBA-2"])
        with freezegun.freeze_time("2024-06-03T00:00:00Z"):
            second = read_output(config, stream_name, SyncMode.incremental, state=[first.state_messages[-1].state])
        assert queries == expected_queries("2024-06-01T00:00:00Z", "2024-06-03T00:00:00Z")
        assert [record.record.data["ShipmentId"] for record in second.records] == ["FBA-2"]
        second_state = second.most_recent_state.stream_state.__dict__
        assert parent_shipment_checkpoint(stream_name, second_state) == {"LastUpdatedBefore": "2024-06-03T00:00:00Z"}


def parent_shipment_checkpoint(stream_name: str, state: dict) -> dict:
    if stream_name == "FbaInboundShipments":
        return state
    return state["parent_state"]["FbaInboundShipments"]
