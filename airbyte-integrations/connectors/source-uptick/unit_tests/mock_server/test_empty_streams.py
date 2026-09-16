# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import UptickRequestBuilder


EMPTY_STREAMS = (
    "creditnotelineitems",
    "defectquotelineitems",
    "remarkevents",
    "majorservices",
    "promptquestions",
    "promptanswers",
    "servicequotefixedlineitems",
    "servicequotedoandchargelineitems",
)

_TOKEN_RESPONSE = {
    "access_token": "tok",
    "expires_in": 3600,
    "token_type": "Bearer",
    "scope": "read write",
}
_CREATED = "2026-01-01T00:00:00Z"
_UPDATED = "2026-01-02T00:00:00Z"
_MODELS = {stream: fields[0] for stream, fields in UptickRequestBuilder.FIELDS.items()}


def _relationship(resource_id: int | None = 1) -> dict[str, Any]:
    if resource_id is None:
        return {"data": None}
    return {"data": {"type": "RelatedResource", "id": resource_id}}


def _record(stream: str, record_id: int) -> dict[str, Any]:
    attributes: dict[str, Any] = {
        "created": _CREATED,
        "updated": _UPDATED,
    }
    relationships: dict[str, Any] = {}
    if stream == "creditnotelineitems":
        attributes.update(
            {
                "deleted": None,
                "account_code": "4000",
                "description": "Credit note line",
                "unit_price": "10.00",
                "quantity": "1.00",
                "subtotal": "10.00",
                "tax": "1.00",
                "total": "11.00",
                "taxcode": "GST",
                "taxrate": "10.00",
            }
        )
        relationships = {"creditnote": _relationship(), "product": _relationship()}
    elif stream == "defectquotelineitems":
        attributes.update(
            {
                "description": "Defect quote line",
                "unit_price": "10.00",
                "cost_price": "8.00",
                "markup": "2.00",
                "quantity": "1.00",
                "taxcode": "GST",
                "taxrate": "10.00",
                "subtotal": "10.00",
                "total": "11.00",
                "gst": "1.00",
                "index": 1,
                "estimated_time": 60,
            }
        )
        relationships = {
            "product": _relationship(),
            "quote": _relationship(),
            "asset": _relationship(),
            "remark": _relationship(),
        }
    elif stream == "remarkevents":
        attributes.update({"event": "updated", "notes": "Remark updated"})
        relationships = {
            "remark": _relationship(),
            "task": _relationship(),
            "servicetask": _relationship(),
            "account": _relationship(),
        }
    elif stream == "majorservices":
        attributes.update({"due": "2026-02-01", "status": "pending"})
        relationships = {
            "asset": _relationship(),
            "routineserviceleveltype": _relationship(),
        }
    elif stream == "promptquestions":
        attributes.update(
            {
                "deleted": None,
                "label": "Question",
                "type": "text",
                "ref": "question_ref",
                "order": 1,
                "config": {},
            }
        )
        relationships = {"section": _relationship()}
    elif stream == "promptanswers":
        attributes.update(
            {
                "value": {"answer": "yes"},
                "performed_date": _UPDATED,
                "guid": "00000000-0000-4000-8000-000000000001",
            }
        )
        relationships = {"question": _relationship(), "answergroup": _relationship()}
    elif stream in {"servicequotefixedlineitems", "servicequotedoandchargelineitems"}:
        attributes.update(
            {
                "description": "Service quote line",
                "quantity": "1.00",
                "unit_price": "10.00",
                "billingcontract_type": "fixed",
                "index": 1,
                "estimated_duration": None,
                "taxcode": "GST",
                "taxrate": "10.00",
                "annual_tax": None,
                "annual_subtotal": "10.00",
            }
        )
        if stream == "servicequotedoandchargelineitems":
            attributes.update({"site_price": "10.00", "service_price": "10.00"})
        relationships = {"servicequote": _relationship()}
    return {
        "type": _MODELS[stream],
        "id": record_id,
        "attributes": attributes,
        "relationships": relationships,
    }


def _response(records: list[dict[str, Any]], next_url: str | None = None) -> HttpResponse:
    return HttpResponse(
        body=json.dumps({"data": records, "links": {"next": next_url}}),
        status_code=200,
    )


def _read(stream: str, sync_mode: SyncMode):
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(stream, sync_mode).build()
    return read(
        get_source(config=config),
        config=config,
        catalog=catalog,
        state=StateBuilder().build(),
    )


def _mock_token(http_mocker: HttpMocker) -> None:
    http_mocker.post(
        HttpRequest(
            url=UptickRequestBuilder.token_endpoint(),
            body=(
                "grant_type=password&client_id=test-client-id&client_secret=test-client-secret" "&username=test-user&password=test-password"
            ),
        ),
        HttpResponse(body=json.dumps(_TOKEN_RESPONSE), status_code=200),
    )


@pytest.mark.parametrize("stream", EMPTY_STREAMS)
@pytest.mark.parametrize("sync_mode", [SyncMode.incremental, SyncMode.full_refresh])
def test_empty_streams_read_two_pages(stream: str, sync_mode: SyncMode) -> None:
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        first_page = UptickRequestBuilder.collection(stream)
        second_page = UptickRequestBuilder.collection(stream, page=2)
        http_mocker.get(
            first_page,
            _response(
                [_record(stream, 1), _record(stream, 2)],
                UptickRequestBuilder.next_page_url(stream),
            ),
        )
        http_mocker.get(second_page, _response([_record(stream, 3)]))

        output = _read(stream, sync_mode)

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [1, 2, 3]
        assert all(message.record.data["updated"] for message in output.records)
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)


@pytest.mark.parametrize("stream", EMPTY_STREAMS)
@pytest.mark.parametrize("sync_mode", [SyncMode.incremental, SyncMode.full_refresh])
def test_empty_streams_complete_without_records(stream: str, sync_mode: SyncMode) -> None:
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        first_page = UptickRequestBuilder.collection(stream)
        http_mocker.get(first_page, _response([]))

        output = _read(stream, sync_mode)

        assert output.errors == []
        assert output.records == []
        assert output.get_stream_statuses(stream)[-1].name == "COMPLETE"
