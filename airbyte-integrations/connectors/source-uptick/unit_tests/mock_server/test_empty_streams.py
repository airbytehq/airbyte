# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any
from unittest.mock import patch

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
_CREATED = "2026-01-01T00:00:00.000000+0000"
_UPDATED = "2026-01-02T00:00:00.000000+0000"
_STATE_CURSOR = "2026-01-01T00:00:00.000000+0000"
_LATEST_UPDATED = "2026-01-03T00:00:00.000000+0000"
_RETRY_STREAM = EMPTY_STREAMS[0]
_MODELS = {stream: fields[0] for stream, fields in UptickRequestBuilder.FIELDS.items()}
_EXPECTED_RELATIONSHIPS = {
    "creditnotelineitems": ("creditnote", "product"),
    "remarkevents": ("remark", "task", "servicetask", "account"),
    "majorservices": ("asset", "routineserviceleveltype"),
    "promptquestions": ("section",),
    "promptanswers": ("question", "answergroup"),
    "servicequotefixedlineitems": ("servicequote",),
    "servicequotedoandchargelineitems": ("servicequote",),
}


def _relationship(resource_id: int | None = 1) -> dict[str, Any]:
    if resource_id is None:
        return {"data": None}
    return {"data": {"type": "RelatedResource", "id": resource_id}}


def _record(
    stream: str,
    record_id: int,
    updated: str = _UPDATED,
    null_relationship: str | None = None,
) -> dict[str, Any]:
    attributes: dict[str, Any] = {
        "created": _CREATED,
        "updated": updated,
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
    if null_relationship is not None:
        relationships[null_relationship] = _relationship(None)
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


def _read(
    stream: str,
    sync_mode: SyncMode = SyncMode.incremental,
    state: Any | None = None,
):
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream(stream, sync_mode).build()
    return read(
        get_source(config=config, state=state),
        config=config,
        catalog=catalog,
        state=StateBuilder().build() if state is None else state,
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


@pytest.mark.parametrize("stream", EMPTY_STREAMS)
def test_incremental_uses_state_cursor(stream: str) -> None:
    state = StateBuilder().with_stream_state(stream, {"updated": _STATE_CURSOR}).build()
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        first_page = UptickRequestBuilder.collection(stream, updatedsince=_STATE_CURSOR)
        http_mocker.get(
            first_page,
            _response(
                [
                    _record(stream, 1, updated="2026-01-02T00:00:00.000000+0000"),
                    _record(stream, 2, updated=_LATEST_UPDATED),
                ]
            ),
        )

        output = _read(stream, state=state)

        assert output.errors == []
        assert [message.record.data["id"] for message in output.records] == [1, 2]
        assert output.most_recent_state.stream_descriptor.name == stream
        assert output.most_recent_state.stream_state.updated == _LATEST_UPDATED
        http_mocker.assert_number_of_calls(first_page, 1)


@pytest.mark.parametrize(
    "status_code",
    [pytest.param(429, id="429"), pytest.param(500, id="500")],
)
def test_retries_on_transient_errors(status_code: int) -> None:
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        first_page = UptickRequestBuilder.collection(_RETRY_STREAM)
        http_mocker.get(
            first_page,
            [
                HttpResponse(
                    body="",
                    status_code=status_code,
                    headers={"Retry-After": "0"},
                ),
                _response([_record(_RETRY_STREAM, 1)]),
            ],
        )

        with patch("time.sleep"):
            output = _read(_RETRY_STREAM)

        assert len(output.records) == 1
        assert output.errors == []
        http_mocker.assert_number_of_calls(first_page, 2)


def test_fails_after_max_retries() -> None:
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        first_page = UptickRequestBuilder.collection(_RETRY_STREAM)
        http_mocker.get(
            first_page,
            [
                HttpResponse(
                    body="",
                    status_code=500,
                    headers={"Retry-After": "0"},
                )
                for _ in range(6)
            ],
        )

        with patch("time.sleep"):
            output = _read(_RETRY_STREAM)

        assert output.records == []
        assert output.get_stream_statuses(_RETRY_STREAM)[-1].name == "INCOMPLETE"
        assert output.errors
        http_mocker.assert_number_of_calls(first_page, 6)


def test_non_retryable_4xx_fails() -> None:
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        first_page = UptickRequestBuilder.collection(_RETRY_STREAM)
        http_mocker.get(
            first_page,
            HttpResponse(body="", status_code=403),
        )

        output = _read(_RETRY_STREAM)

        assert output.records == []
        assert output.get_stream_statuses(_RETRY_STREAM)[-1].name == "INCOMPLETE"
        assert output.errors
        assert output.get_formatted_error_message()
        http_mocker.assert_number_of_calls(first_page, 1)


@pytest.mark.parametrize("stream", EMPTY_STREAMS)
def test_flattens_jsonapi_record(stream: str) -> None:
    relationship_names = _EXPECTED_RELATIONSHIPS[stream]
    first_relationship = relationship_names[0]
    records = [
        _record(stream, 1),
        _record(stream, 2, null_relationship=first_relationship),
    ]
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        first_page = UptickRequestBuilder.collection(stream)
        http_mocker.get(first_page, _response(records))

        output = _read(stream)

        assert output.errors == []
        assert len(output.records) == 2
        for record_number, message in enumerate(output.records, start=1):
            record = message.record.data
            assert record["id"] == record_number
            assert record["created"] == _CREATED
            assert record["updated"] == _UPDATED
            assert "attributes" in record
            assert "relationships" in record
            for relationship_name in relationship_names:
                field_name = f"{relationship_name}_id"
                if record_number == 2 and relationship_name == first_relationship:
                    assert field_name not in record
                else:
                    assert record[field_name] == 1
            if "deleted" in records[record_number - 1]["attributes"]:
                # deleted is ["string","null"]; the protocol serializer drops top-level None values
                assert "deleted" not in record
        if stream == "creditnotelineitems":
            record = output.records[0].record.data
            assert record["account_code"] == "4000"
            assert record["description"] == "Credit note line"
            assert record["taxcode"] == "GST"
        assert output.is_not_in_logs("does not conform")


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Manifest AddFields renders attributes through Jinja, which literal_evals decimal strings "
        "('10.00' -> 10.0) and null strings to the text 'None'; tracked as a follow-up connector fix"
    ),
)
def test_creditnotelineitems_record_values_round_trip() -> None:
    stream = "creditnotelineitems"
    record = _record(stream, 1)
    record["attributes"]["description"] = None
    with HttpMocker() as http_mocker:
        _mock_token(http_mocker)
        first_page = UptickRequestBuilder.collection(stream)
        http_mocker.get(first_page, _response([record]))

        output = _read(stream)

        assert output.errors == []
        emitted = {k: v for k, v in output.records[0].record.data.items() if k not in ("attributes", "relationships")}
        assert emitted == {
            "type": "CreditNoteLineItem",
            "id": 1,
            "created": _CREATED,
            "updated": _UPDATED,
            "account_code": "4000",
            "unit_price": "10.00",
            "quantity": "1.00",
            "subtotal": "10.00",
            "tax": "1.00",
            "total": "11.00",
            "taxcode": "GST",
            "taxrate": "10.00",
            "creditnote_id": 1,
            "product_id": 1,
        }
