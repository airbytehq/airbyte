#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import asyncio
import json
from unittest.mock import MagicMock, patch

import pytest
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, AirbyteRecordMessage, Level, Type
from connector_builder.generated.models.http_request import HttpRequest
from connector_builder.generated.models.http_response import HttpResponse
from connector_builder.generated.models.stream_read import StreamRead
from connector_builder.generated.models.stream_read_pages import StreamReadPages
from connector_builder.generated.models.stream_read_request_body import StreamReadRequestBody
from connector_builder.generated.models.streams_list_read import StreamsListRead
from connector_builder.generated.models.streams_list_read_streams import StreamsListReadStreams
from connector_builder.generated.models.streams_list_request_body import StreamsListRequestBody
from connector_builder.impl.default_api import DefaultApiImpl
from fastapi import HTTPException

MANIFEST = {
    "version": "0.1.0",
    "definitions": {
        "selector": {"extractor": {"field_pointer": ["items"]}},
        "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET"},
        "retriever": {
            "record_selector": {"extractor": {"field_pointer": ["items"]}},
            "paginator": {"type": "NoPagination"},
            "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET"},
        },
        "hashiras_stream": {
            "retriever": {
                "record_selector": {"extractor": {"field_pointer": ["items"]}},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET"},
            },
            "$options": {"name": "hashiras", "path": "/hashiras"},
        },
        "breathing_techniques_stream": {
            "retriever": {
                "record_selector": {"extractor": {"field_pointer": ["items"]}},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET"},
            },
            "$options": {"name": "breathing-techniques", "path": "/breathing_techniques"},
        },
    },
    "streams": [
        {
            "retriever": {
                "record_selector": {"extractor": {"field_pointer": ["items"]}},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET"},
            },
            "$options": {"name": "hashiras", "path": "/hashiras"},
        },
        {
            "retriever": {
                "record_selector": {"extractor": {"field_pointer": ["items"]}},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET"},
            },
            "$options": {"name": "breathing-techniques", "path": "/breathing_techniques"},
        },
    ],
    "check": {"stream_names": ["hashiras"], "class_name": "airbyte_cdk.sources.declarative.checks.check_stream.CheckStream"},
}

CONFIG = {"rank": "upper-six"}


def request_log_message(request: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=f"request:{json.dumps(request)}"))


def response_log_message(response: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=f"response:{json.dumps(response)}"))


def record_message(stream: str, data: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=1234))


def test_list_streams():
    expected_streams = [
        StreamsListReadStreams(name="hashiras", url="https://demonslayers.com/api/v1/hashiras"),
        StreamsListReadStreams(name="breathing-techniques", url="https://demonslayers.com/api/v1/breathing_techniques"),
    ]

    api = DefaultApiImpl()
    streams_list_request_body = StreamsListRequestBody(manifest=MANIFEST, config=CONFIG)
    loop = asyncio.get_event_loop()
    actual_streams = loop.run_until_complete(api.list_streams(streams_list_request_body))

    for i, expected_stream in enumerate(expected_streams):
        assert actual_streams.streams[i] == expected_stream


def test_list_streams_with_interpolated_urls():
    manifest = {
        "version": "0.1.0",
        "streams": [
            {
                "retriever": {
                    "record_selector": {"extractor": {"field_pointer": ["items"]}},
                    "paginator": {"type": "NoPagination"},
                    "requester": {"url_base": "https://{{ config['rank'] }}.muzan.com/api/v1/", "http_method": "GET"},
                },
                "$options": {"name": "demons", "path": "/demons"},
            }
        ],
        "check": {"stream_names": ["demons"], "class_name": "airbyte_cdk.sources.declarative.checks.check_stream.CheckStream"},
    }

    expected_streams = StreamsListRead(streams=[StreamsListReadStreams(name="demons", url="https://upper-six.muzan.com/api/v1/demons")])

    api = DefaultApiImpl()
    streams_list_request_body = StreamsListRequestBody(manifest=manifest, config=CONFIG)
    loop = asyncio.get_event_loop()
    actual_streams = loop.run_until_complete(api.list_streams(streams_list_request_body))

    assert actual_streams == expected_streams


def test_list_streams_with_unresolved_interpolation():
    manifest = {
        "version": "0.1.0",
        "streams": [
            {
                "retriever": {
                    "record_selector": {"extractor": {"field_pointer": ["items"]}},
                    "paginator": {"type": "NoPagination"},
                    "requester": {"url_base": "https://{{ config['not_in_config'] }}.muzan.com/api/v1/", "http_method": "GET"},
                },
                "$options": {"name": "demons", "path": "/demons"},
            }
        ],
        "check": {"stream_names": ["demons"], "class_name": "airbyte_cdk.sources.declarative.checks.check_stream.CheckStream"},
    }

    # The interpolated string {{ config['not_in_config'] }} doesn't resolve to anything so it ends up blank during interpolation
    expected_streams = StreamsListRead(streams=[StreamsListReadStreams(name="demons", url="https://.muzan.com/api/v1/demons")])

    api = DefaultApiImpl()

    streams_list_request_body = StreamsListRequestBody(manifest=manifest, config=CONFIG)
    loop = asyncio.get_event_loop()
    actual_streams = loop.run_until_complete(api.list_streams(streams_list_request_body))

    assert actual_streams == expected_streams


def test_read_stream():
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "body": {"custom": "field"},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}
    expected_pages = [
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body={"name": "field"}),
            records=[{"name": "Shinobu Kocho"}, {"name": "Muichiro Tokito"}],
        ),
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body={"name": "field"}),
            records=[{"name": "Mitsuri Kanroji"}],
        ),
    ]

    mock_source_adapter = MagicMock()
    mock_source_adapter.read_stream.return_value = [
        request_log_message(request),
        response_log_message(response),
        record_message("hashiras", {"name": "Shinobu Kocho"}),
        record_message("hashiras", {"name": "Muichiro Tokito"}),
        request_log_message(request),
        response_log_message(response),
        record_message("hashiras", {"name": "Mitsuri Kanroji"}),
    ]

    with patch.object(DefaultApiImpl, "_create_low_code_adapter", return_value=mock_source_adapter):
        api = DefaultApiImpl()

        loop = asyncio.get_event_loop()
        actual_response: StreamRead = loop.run_until_complete(
            api.read_stream(StreamReadRequestBody(manifest=MANIFEST, config=CONFIG, stream="hashiras"))
        )

        single_slice = actual_response.slices[0]
        for i, actual_page in enumerate(single_slice.pages):
            assert actual_page == expected_pages[i]


def test_read_stream_with_logs():
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "body": {"custom": "field"},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}
    expected_pages = [
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body={"name": "field"}),
            records=[{"name": "Shinobu Kocho"}, {"name": "Muichiro Tokito"}],
        ),
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body={"name": "field"}),
            records=[{"name": "Mitsuri Kanroji"}],
        ),
    ]
    expected_logs = [
        {"message": "log message before the request"},
        {"message": "log message during the page"},
        {"message": "log message after the response"},
    ]

    mock_source_adapter = MagicMock()
    mock_source_adapter.read_stream.return_value = [
        AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="log message before the request")),
        request_log_message(request),
        response_log_message(response),
        record_message("hashiras", {"name": "Shinobu Kocho"}),
        AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="log message during the page")),
        record_message("hashiras", {"name": "Muichiro Tokito"}),
        AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="log message after the response")),
    ]

    with patch.object(DefaultApiImpl, "_create_low_code_adapter", return_value=mock_source_adapter):
        api = DefaultApiImpl()

        loop = asyncio.get_event_loop()
        actual_response: StreamRead = loop.run_until_complete(
            api.read_stream(StreamReadRequestBody(manifest=MANIFEST, config=CONFIG, stream="hashiras"))
        )

        single_slice = actual_response.slices[0]
        for i, actual_page in enumerate(single_slice.pages):
            assert actual_page == expected_pages[i]

        for i, actual_log in enumerate(actual_response.logs):
            assert actual_log == expected_logs[i]


def test_read_stream_no_records():
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "body": {"custom": "field"},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}
    expected_pages = [
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body={"name": "field"}),
            records=[],
        ),
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body={"name": "field"}),
            records=[],
        ),
    ]

    mock_source_adapter = MagicMock()
    mock_source_adapter.read_stream.return_value = [
        request_log_message(request),
        response_log_message(response),
        request_log_message(request),
        response_log_message(response),
    ]

    with patch.object(DefaultApiImpl, "_create_low_code_adapter", return_value=mock_source_adapter):
        api = DefaultApiImpl()

        loop = asyncio.get_event_loop()
        actual_response: StreamRead = loop.run_until_complete(
            api.read_stream(StreamReadRequestBody(manifest=MANIFEST, config=CONFIG, stream="hashiras"))
        )

        single_slice = actual_response.slices[0]
        for i, actual_page in enumerate(single_slice.pages):
            assert actual_page == expected_pages[i]


def test_invalid_manifest():
    invalid_manifest = {
        "version": "0.1.0",
        "definitions": {
            "selector": {"extractor": {"field_pointer": ["items"]}},
            "requester": {"http_method": "GET"},
            "retriever": {
                "record_selector": {"extractor": {"field_pointer": ["items"]}},
                "paginator": {"type": "NoPagination"},
                "requester": {"http_method": "GET"},
            },
            "hashiras_stream": {
                "retriever": {
                    "record_selector": {"extractor": {"field_pointer": ["items"]}},
                    "paginator": {"type": "NoPagination"},
                    "requester": {"http_method": "GET"},
                },
                "$options": {"name": "hashiras", "path": "/hashiras"},
            },
        },
        "check": {"stream_names": ["hashiras"], "class_name": "airbyte_cdk.sources.declarative.checks.check_stream.CheckStream"},
    }

    expected_status_code = 400

    api = DefaultApiImpl()
    loop = asyncio.get_event_loop()
    with pytest.raises(HTTPException) as actual_exception:
        loop.run_until_complete(api.read_stream(StreamReadRequestBody(manifest=invalid_manifest, config={}, stream="hashiras")))

    assert actual_exception.value.status_code == expected_status_code


def test_read_stream_invalid_group_format():
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}

    mock_source_adapter = MagicMock()
    mock_source_adapter.read_stream.return_value = [
        response_log_message(response),
        record_message("hashiras", {"name": "Shinobu Kocho"}),
        record_message("hashiras", {"name": "Muichiro Tokito"}),
    ]

    with patch.object(DefaultApiImpl, "_create_low_code_adapter", return_value=mock_source_adapter):
        api = DefaultApiImpl()

        loop = asyncio.get_event_loop()
        with pytest.raises(HTTPException) as actual_exception:
            loop.run_until_complete(api.read_stream(StreamReadRequestBody(manifest=MANIFEST, config=CONFIG, stream="hashiras")))

        assert actual_exception.value.status_code == 400


def test_read_stream_returns_error_if_stream_does_not_exist():
    expected_status_code = 400

    api = DefaultApiImpl()
    loop = asyncio.get_event_loop()
    with pytest.raises(HTTPException) as actual_exception:
        loop.run_until_complete(api.read_stream(StreamReadRequestBody(manifest=MANIFEST, config={}, stream="not_in_manifest")))

    assert actual_exception.value.status_code == expected_status_code


@pytest.mark.parametrize(
    "log_message, expected_request",
    [
        pytest.param(
            'request:{"url": "https://nichirin.com/v1/swords?color=orange", "http_method": "PUT", "headers": {"field": "name"}, "body":{"key": "value"}}',
            HttpRequest(
                url="https://nichirin.com/v1/swords", parameters={"color": ["orange"]}, headers={"field": "name"}, body={"key": "value"},
                http_method="PUT",
            ),
            id="test_create_request_with_all_fields",
        ),
        pytest.param(
            'request:{"url": "https://nichirin.com/v1/swords?color=orange", "http_method": "GET", "headers": {"field": "name"}}',
            HttpRequest(url="https://nichirin.com/v1/swords", parameters={"color": ["orange"]}, headers={"field": "name"},
                        http_method="GET"),
            id="test_create_request_with_no_body",
        ),
        pytest.param(
            'request:{"url": "https://nichirin.com/v1/swords?color=orange", "http_method": "PUT", "body":{"key": "value"}}',
            HttpRequest(url="https://nichirin.com/v1/swords", parameters={"color": ["orange"]}, body={"key": "value"}, http_method="PUT"),
            id="test_create_request_with_no_headers",
        ),
        pytest.param(
            'request:{"url": "https://nichirin.com/v1/swords", "http_method": "PUT", "headers": {"field": "name"}, "body":{"key": "value"}}',
            HttpRequest(url="https://nichirin.com/v1/swords", headers={"field": "name"}, body={"key": "value"}, http_method="PUT"),
            id="test_create_request_with_no_parameters",
        ),
        pytest.param("request:{invalid_json: }", None, id="test_invalid_json_still_does_not_crash"),
        pytest.param("just a regular log message", None, id="test_no_request:_prefix_does_not_crash"),
    ],
)
def test_create_request_from_log_message(log_message, expected_request):
    airbyte_log_message = AirbyteLogMessage(level=Level.INFO, message=log_message)
    api = DefaultApiImpl()
    actual_request = api._create_request_from_log_message(airbyte_log_message)

    assert actual_request == expected_request


@pytest.mark.parametrize(
    "log_message, expected_response",
    [
        pytest.param(
            {"status_code": 200, "headers": {"field": "name"}, "body": '{"id":"fire", "owner": "kyojuro_rengoku"}'},
            HttpResponse(status=200, headers={"field": "name"}, body={"id": "fire", "owner": "kyojuro_rengoku"}),
            id="test_create_response_with_all_fields",
        ),
        pytest.param(
            {"status_code": 200, "headers": {"field": "name"}},
            HttpResponse(status=200, body={}, headers={"field": "name"}),
            id="test_create_response_with_no_body",
        ),
        pytest.param(
            {"status_code": 200, "body": '{"id":"fire", "owner": "kyojuro_rengoku"}'},
            HttpResponse(status=200, body={"id": "fire", "owner": "kyojuro_rengoku"}),
            id="test_create_response_with_no_headers",
        ),
        pytest.param("request:{invalid_json: }", None, id="test_invalid_json_still_does_not_crash"),
        pytest.param("just a regular log message", None, id="test_no_response:_prefix_does_not_crash"),
    ],
)
def test_create_response_from_log_message(log_message, expected_response):
    if isinstance(log_message, str):
        response_message = log_message
    else:
        response_message = f"response:{json.dumps(log_message)}"

    airbyte_log_message = AirbyteLogMessage(level=Level.INFO, message=response_message)
    api = DefaultApiImpl()
    actual_response = api._create_response_from_log_message(airbyte_log_message)

    assert actual_response == expected_response
