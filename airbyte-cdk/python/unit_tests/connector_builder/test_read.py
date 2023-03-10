#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncio
import json
from unittest.mock import MagicMock

import pytest
from pydantic.error_wrappers import ValidationError

from airbyte_cdk.models import Level, Type
from connector_builder.connector_builder_handler import *

MAX_PAGES_PER_SLICE = 4
MAX_SLICES = 3

MANIFEST = {
    "version": "0.1.0",
    "type": "DeclarativeSource",
    "definitions": {
        "selector": {"extractor": {"field_path": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
        "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "DeclarativeSource"},
        "retriever": {
            "type": "DeclarativeSource",
            "record_selector": {"extractor": {"field_path": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
            "paginator": {"type": "NoPagination"},
            "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
        },
        "hashiras_stream": {
            "retriever": {
                "type": "DeclarativeSource",
                "record_selector": {"extractor": {"field_path": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$parameters": {"name": "hashiras", "path": "/hashiras"},
        },
        "breathing_techniques_stream": {
            "retriever": {
                "type": "DeclarativeSource",
                "record_selector": {"extractor": {"field_path": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$parameters": {"name": "breathing-techniques", "path": "/breathing_techniques"},
        },
    },
    "streams": [
        {
            "type": "DeclarativeStream",
            "retriever": {
                "type": "SimpleRetriever",
                "record_selector": {"extractor": {"field_path": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$parameters": {"name": "hashiras", "path": "/hashiras"},
        },
        {
            "type": "DeclarativeStream",
            "retriever": {
                "type": "SimpleRetriever",
                "record_selector": {"extractor": {"field_path": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$parameters": {"name": "breathing-techniques", "path": "/breathing_techniques"},
        },
    ],
    "check": {"stream_names": ["hashiras"], "type": "CheckStream"},
}

CONFIG = {"rank": "upper-six"}

def test_read_stream():
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "http_method": "GET",
        "body": {"custom": "field"},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}', "http_method": "GET"}
    expected_schema = {"$schema": "http://json-schema.org/schema#", "properties": {"name": {"type": "string"}}, "type": "object"}
    expected_pages = [
        {
            "request":{
                "url":"https://demonslayers.com/api/v1/hashiras",
                "parameters":{"era": ["taisho"]},
                "headers": {"Content-Type": "application/json"},
                "body":{"custom": "field"},
                "http_method":"GET",
            },
            "response":{"status":200, "headers":{"field": "value"}, "body":'{"name": "field"}'},
            "records":[{"name": "Shinobu Kocho"}, {"name": "Muichiro Tokito"}],
        },
        {
            "request":{
                "url": "https://demonslayers.com/api/v1/hashiras",
                "parameters": {"era": ["taisho"]},
                "headers": {"Content-Type": "application/json"},
                "body":{"custom": "field"},
                "http_method":"GET",
            },
            "response":{"status": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'},
            "records":[{"name": "Mitsuri Kanroji"}],
        },
    ]

    mock_source = make_mock_source(
        iter(
            [
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Mitsuri Kanroji"}),
            ]
        )
    )

    connector_builder_handler = ConnectorBuilderHandler(MAX_PAGES_PER_SLICE, MAX_SLICES)
    actual_response: AirbyteMessage = connector_builder_handler.read_stream(source=mock_source, config=CONFIG, stream="hashiras")
    record = actual_response.record
    stream_read_object: StreamRead = StreamRead(**record.data)
    stream_read_object.slices = [StreamReadSlicesInner(**s) for s in stream_read_object.slices]
    assert stream_read_object.inferred_schema == expected_schema

    single_slice = stream_read_object.slices[0]
    for i, actual_page in enumerate(single_slice.pages):
        assert actual_page == expected_pages[i]

def test_read_stream_with_logs():
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "body": {"custom": "field"},
        "http_method": "GET",
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}
    expected_pages = [
        {
            "request":{
                "url": "https://demonslayers.com/api/v1/hashiras",
                "parameters": {"era": ["taisho"]},
                "headers": {"Content-Type": "application/json"},
                "body": {"custom": "field"},
                "http_method": "GET",
            },
            "response":{"status": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'},
            "records":[{"name": "Shinobu Kocho"}, {"name": "Muichiro Tokito"}],
        },
        {
            "request":{
                "url":"https://demonslayers.com/api/v1/hashiras",
                "parameters": {"era": ["taisho"]},
                "headers": {"Content-Type": "application/json"},
                "body": {"custom": "field"},
                "http_method": "GET",
            },
            "response":{"status":200, "headers":{"field": "value"}, "body": '{"name": "field"}'},
            "records":[{"name": "Mitsuri Kanroji"}],
        },
    ]
    expected_logs = [
        {"message": "log message before the request"},
        {"message": "log message during the page"},
        {"message": "log message after the response"},
    ]

    mock_source = make_mock_source(
        iter(
            [
                AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="log message before the request")),
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="log message during the page")),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="log message after the response")),
            ]
        )
    )

    connector_builder_handler = ConnectorBuilderHandler(MAX_PAGES_PER_SLICE, MAX_SLICES)

    actual_response: AirbyteMessage = connector_builder_handler.read_stream(source=mock_source, config=CONFIG, stream="hashiras")
    record = actual_response.record
    stream_read_object: StreamRead = StreamRead(**record.data)
    stream_read_object.slices = [StreamReadSlicesInner(**s) for s in stream_read_object.slices]

    single_slice = stream_read_object.slices[0]
    for i, actual_page in enumerate(single_slice.pages):
        assert actual_page == expected_pages[i]

    for i, actual_log in enumerate(stream_read_object.logs):
        assert actual_log == expected_logs[i]

@pytest.mark.parametrize(
    "request_record_limit, max_record_limit",
    [
        pytest.param(1, 3, id="test_create_request_with_record_limit"),
        pytest.param(3, 1, id="test_create_request_record_limit_exceeds_max"),
    ],
)
def test_read_stream_record_limit(request_record_limit, max_record_limit):
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "body": {"custom": "field"},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}
    mock_source = make_mock_source(
        iter(
            [
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Mitsuri Kanroji"}),
                response_log_message(response),
            ]
        )
    )
    n_records = 2
    record_limit = min(request_record_limit, max_record_limit)

    api = ConnectorBuilderHandler(MAX_PAGES_PER_SLICE, MAX_SLICES, max_record_limit=max_record_limit)
    actual_response: AirbyteMessage =  api.read_stream(mock_source, config=CONFIG, stream="hashiras", record_limit=request_record_limit)
    record = actual_response.record
    stream_read_object: StreamRead = StreamRead(**record.data)
    stream_read_object.slices = [StreamReadSlicesInner(**s) for s in stream_read_object.slices]
    single_slice = stream_read_object.slices[0]
    total_records = 0
    for i, actual_page in enumerate(single_slice.pages):
        total_records += len(actual_page["records"])
    assert total_records == min([record_limit, n_records])

@pytest.mark.parametrize(
    "max_record_limit",
    [
        pytest.param(2, id="test_create_request_no_record_limit"),
        pytest.param(1, id="test_create_request_no_record_limit_n_records_exceed_max"),
    ],
)
def test_read_stream_default_record_limit(max_record_limit):
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "body": {"custom": "field"},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}
    mock_source = make_mock_source(
        iter(
            [
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Mitsuri Kanroji"}),
                response_log_message(response),
            ]
        )
    )
    n_records = 2

    api = ConnectorBuilderHandler(MAX_PAGES_PER_SLICE, MAX_SLICES, max_record_limit=max_record_limit)
    actual_response: AirbyteMessage = api.read_stream(source=mock_source, config=CONFIG, stream="hashiras")
    record = actual_response.record
    stream_read_object: StreamRead = StreamRead(**record.data)
    stream_read_object.slices = [StreamReadSlicesInner(**s) for s in stream_read_object.slices]
    single_slice = stream_read_object.slices[0]
    total_records = 0
    for i, actual_page in enumerate(single_slice.pages):
        total_records += len(actual_page["records"])
    assert total_records == min([max_record_limit, n_records])

def test_read_stream_limit_0():
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "body": {"custom": "field"},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}
    mock_source = make_mock_source(
        iter(
            [
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Mitsuri Kanroji"}),
                response_log_message(response),
            ]
        )
    )
    api = ConnectorBuilderHandler(MAX_PAGES_PER_SLICE, MAX_SLICES)

    with pytest.raises(ValueError):
        api.read_stream(source=mock_source, config=CONFIG, stream="hashiras", record_limit=0)

def test_read_stream_no_records():
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "body": {"custom": "field"},
        "http_method": "GET",
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}
    expected_pages = [
        {
            "request":{
                "url":"https://demonslayers.com/api/v1/hashiras",
                "parameters": {"era": ["taisho"]},
                "headers": {"Content-Type": "application/json"},
                "body": {"custom": "field"},
                "http_method": "GET",
            },
            "response":{"status": 200, "headers": {"field": "value"}, "body":'{"name": "field"}'},
            "records":[],
        },
        {
            "request":{
                "url": "https://demonslayers.com/api/v1/hashiras",
                "parameters": {"era": ["taisho"]},
                "headers": {"Content-Type": "application/json"},
                "body": {"custom": "field"},
                "http_method": "GET",
            },
            "response": {"status":200, "headers":{"field": "value"}, "body": '{"name": "field"}'},
            "records": [],
        },
    ]

    mock_source = make_mock_source(
        iter(
            [
                request_log_message(request),
                response_log_message(response),
                request_log_message(request),
                response_log_message(response),
            ]
        )
    )

    api = ConnectorBuilderHandler(MAX_PAGES_PER_SLICE, MAX_SLICES)

    actual_response: AirbyteMessage = api.read_stream(source=mock_source, config=CONFIG, stream="hashiras")
    record = actual_response.record
    stream_read_object: StreamRead = StreamRead(**record.data)
    stream_read_object.slices = [StreamReadSlicesInner(**s) for s in stream_read_object.slices]

    single_slice = stream_read_object.slices[0]
    for i, actual_page in enumerate(single_slice.pages):
        assert actual_page == expected_pages[i]

def test_read_stream_invalid_group_format():
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}

    mock_source = make_mock_source(
        iter(
            [
                response_log_message(response),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
            ]
        )
    )

    api = ConnectorBuilderHandler(MAX_PAGES_PER_SLICE, MAX_SLICES)

    with pytest.raises(ValueError) as actual_exception:
        api.read_stream(source=mock_source, config=CONFIG, stream="hashiras")

def make_mock_source(return_value: Iterator) -> MagicMock:
    mock_source = MagicMock()
    mock_source.read.return_value = return_value
    return mock_source

def request_log_message(request: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=f"request:{json.dumps(request)}"))


def response_log_message(response: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=f"response:{json.dumps(response)}"))


def record_message(stream: str, data: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=1234))


def slice_message() -> AirbyteMessage:
    return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message='slice:{"key": "value"}'))

