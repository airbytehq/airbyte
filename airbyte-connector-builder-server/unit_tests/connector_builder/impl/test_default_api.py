#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import asyncio
import json
from typing import Iterator
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, AirbyteRecordMessage, Level, Type
from connector_builder.generated.models.http_request import HttpRequest
from connector_builder.generated.models.http_response import HttpResponse
from connector_builder.generated.models.resolve_manifest import ResolveManifest
from connector_builder.generated.models.resolve_manifest_request_body import ResolveManifestRequestBody
from connector_builder.generated.models.stream_read import StreamRead
from connector_builder.generated.models.stream_read_pages import StreamReadPages
from connector_builder.generated.models.stream_read_request_body import StreamReadRequestBody
from connector_builder.generated.models.streams_list_read import StreamsListRead
from connector_builder.generated.models.streams_list_read_streams import StreamsListReadStreams
from connector_builder.generated.models.streams_list_request_body import StreamsListRequestBody
from connector_builder.impl.default_api import DefaultApiImpl
from connector_builder.impl.low_code_cdk_adapter import LowCodeSourceAdapterFactory
from fastapi import HTTPException
from pydantic.error_wrappers import ValidationError

MAX_PAGES_PER_SLICE = 4
MAX_SLICES = 3

MANIFEST = {
    "version": "0.1.0",
    "type": "DeclarativeSource",
    "definitions": {
        "selector": {"extractor": {"field_pointer": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
        "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "DeclarativeSource"},
        "retriever": {
            "type": "DeclarativeSource",
            "record_selector": {"extractor": {"field_pointer": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
            "paginator": {"type": "NoPagination"},
            "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
        },
        "hashiras_stream": {
            "retriever": {
                "type": "DeclarativeSource",
                "record_selector": {"extractor": {"field_pointer": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$options": {"name": "hashiras", "path": "/hashiras"},
        },
        "breathing_techniques_stream": {
            "retriever": {
                "type": "DeclarativeSource",
                "record_selector": {"extractor": {"field_pointer": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$options": {"name": "breathing-techniques", "path": "/breathing_techniques"},
        },
    },
    "streams": [
        {
            "type": "DeclarativeStream",
            "retriever": {
                "type": "SimpleRetriever",
                "record_selector": {"extractor": {"field_pointer": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$options": {"name": "hashiras", "path": "/hashiras"},
        },
        {
            "type": "DeclarativeStream",
            "retriever": {
                "type": "SimpleRetriever",
                "record_selector": {"extractor": {"field_pointer": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$options": {"name": "breathing-techniques", "path": "/breathing_techniques"},
        },
    ],
    "check": {"stream_names": ["hashiras"], "type": "CheckStream"},
}

CONFIG = {"rank": "upper-six"}


def request_log_message(request: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=f"request:{json.dumps(request)}"))


def response_log_message(response: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=f"response:{json.dumps(response)}"))


def record_message(stream: str, data: dict) -> AirbyteMessage:
    return AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data=data, emitted_at=1234))


def slice_message() -> AirbyteMessage:
    return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message='slice:{"key": "value"}'))


def test_list_streams():
    expected_streams = [
        StreamsListReadStreams(name="hashiras", url="https://demonslayers.com/api/v1/hashiras"),
        StreamsListReadStreams(name="breathing-techniques", url="https://demonslayers.com/api/v1/breathing_techniques"),
    ]

    api = DefaultApiImpl(LowCodeSourceAdapterFactory(MAX_PAGES_PER_SLICE, MAX_SLICES), MAX_PAGES_PER_SLICE, MAX_SLICES)
    streams_list_request_body = StreamsListRequestBody(manifest=MANIFEST, config=CONFIG)
    loop = asyncio.get_event_loop()
    actual_streams = loop.run_until_complete(api.list_streams(streams_list_request_body))

    for i, expected_stream in enumerate(expected_streams):
        assert actual_streams.streams[i] == expected_stream


def test_list_streams_with_interpolated_urls():
    manifest = {
        "version": "0.1.0",
        "type": "DeclarativeSource",
        "streams": [
            {
                "type": "DeclarativeStream",
                "retriever": {
                    "type": "SimpleRetriever",
                    "record_selector": {"extractor": {"field_pointer": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                    "paginator": {"type": "NoPagination"},
                    "requester": {
                        "url_base": "https://{{ config['rank'] }}.muzan.com/api/v1/",
                        "http_method": "GET",
                        "type": "HttpRequester",
                    },
                },
                "$options": {"name": "demons", "path": "/demons"},
            }
        ],
        "check": {"stream_names": ["demons"], "type": "CheckStream"},
    }

    expected_streams = StreamsListRead(streams=[StreamsListReadStreams(name="demons", url="https://upper-six.muzan.com/api/v1/demons")])

    api = DefaultApiImpl(LowCodeSourceAdapterFactory(MAX_PAGES_PER_SLICE, MAX_SLICES), MAX_PAGES_PER_SLICE, MAX_SLICES)
    streams_list_request_body = StreamsListRequestBody(manifest=manifest, config=CONFIG)
    loop = asyncio.get_event_loop()
    actual_streams = loop.run_until_complete(api.list_streams(streams_list_request_body))

    assert actual_streams == expected_streams


def test_list_streams_with_unresolved_interpolation():
    manifest = {
        "version": "0.1.0",
        "type": "DeclarativeSource",
        "streams": [
            {
                "type": "DeclarativeStream",
                "retriever": {
                    "type": "SimpleRetriever",
                    "record_selector": {"extractor": {"field_pointer": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                    "paginator": {"type": "NoPagination"},
                    "requester": {
                        "url_base": "https://{{ config['not_in_config'] }}.muzan.com/api/v1/",
                        "http_method": "GET",
                        "type": "HttpRequester",
                    },
                },
                "$options": {"name": "demons", "path": "/demons"},
            }
        ],
        "check": {"stream_names": ["demons"], "type": "CheckStream"},
    }

    # The interpolated string {{ config['not_in_config'] }} doesn't resolve to anything so it ends up blank during interpolation
    expected_streams = StreamsListRead(streams=[StreamsListReadStreams(name="demons", url="https://.muzan.com/api/v1/demons")])

    api = DefaultApiImpl(LowCodeSourceAdapterFactory(MAX_PAGES_PER_SLICE, MAX_SLICES), MAX_PAGES_PER_SLICE, MAX_SLICES)

    streams_list_request_body = StreamsListRequestBody(manifest=manifest, config=CONFIG)
    loop = asyncio.get_event_loop()
    actual_streams = loop.run_until_complete(api.list_streams(streams_list_request_body))

    assert actual_streams == expected_streams


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
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
                http_method="GET",
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
                http_method="GET",
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body={"name": "field"}),
            records=[{"name": "Mitsuri Kanroji"}],
        ),
    ]

    mock_source_adapter_cls = make_mock_adapter_factory(
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

    api = DefaultApiImpl(mock_source_adapter_cls, MAX_PAGES_PER_SLICE, MAX_SLICES)

    loop = asyncio.get_event_loop()
    actual_response: StreamRead = loop.run_until_complete(
        api.read_stream(StreamReadRequestBody(manifest=MANIFEST, config=CONFIG, stream="hashiras"))
    )
    assert actual_response.inferred_schema == expected_schema

    single_slice = actual_response.slices[0]
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
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
                http_method="GET",
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
                http_method="GET",
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

    mock_source_adapter_cls = make_mock_adapter_factory(
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

    api = DefaultApiImpl(mock_source_adapter_cls, MAX_PAGES_PER_SLICE, MAX_SLICES)

    loop = asyncio.get_event_loop()
    actual_response: StreamRead = loop.run_until_complete(
        api.read_stream(StreamReadRequestBody(manifest=MANIFEST, config=CONFIG, stream="hashiras"))
    )

    single_slice = actual_response.slices[0]
    for i, actual_page in enumerate(single_slice.pages):
        assert actual_page == expected_pages[i]

    for i, actual_log in enumerate(actual_response.logs):
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
    mock_source_adapter_cls = make_mock_adapter_factory(
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

    api = DefaultApiImpl(mock_source_adapter_cls, MAX_PAGES_PER_SLICE, MAX_SLICES, max_record_limit=max_record_limit)
    loop = asyncio.get_event_loop()
    actual_response: StreamRead = loop.run_until_complete(
        api.read_stream(StreamReadRequestBody(manifest=MANIFEST, config=CONFIG, stream="hashiras", record_limit=request_record_limit))
    )
    single_slice = actual_response.slices[0]
    total_records = 0
    for i, actual_page in enumerate(single_slice.pages):
        total_records += len(actual_page.records)
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
    mock_source_adapter_cls = make_mock_adapter_factory(
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

    api = DefaultApiImpl(mock_source_adapter_cls, MAX_PAGES_PER_SLICE, MAX_SLICES, max_record_limit=max_record_limit)
    loop = asyncio.get_event_loop()
    actual_response: StreamRead = loop.run_until_complete(
        api.read_stream(StreamReadRequestBody(manifest=MANIFEST, config=CONFIG, stream="hashiras"))
    )
    single_slice = actual_response.slices[0]
    total_records = 0
    for i, actual_page in enumerate(single_slice.pages):
        total_records += len(actual_page.records)
    assert total_records == min([max_record_limit, n_records])


def test_read_stream_limit_0():
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "body": {"custom": "field"},
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}
    mock_source_adapter_cls = make_mock_adapter_factory(
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
    api = DefaultApiImpl(mock_source_adapter_cls, MAX_PAGES_PER_SLICE, MAX_SLICES)
    loop = asyncio.get_event_loop()

    with pytest.raises(ValidationError):
        loop.run_until_complete(api.read_stream(StreamReadRequestBody(manifest=MANIFEST, config=CONFIG, stream="hashiras", record_limit=0)))
        loop.run_until_complete(api.read_stream(StreamReadRequestBody(manifest=MANIFEST, config=CONFIG, stream="hashiras")))


def test_read_stream_no_records():
    request = {
        "url": "https://demonslayers.com/api/v1/hashiras?era=taisho",
        "headers": {"Content-Type": "application/json"},
        "body": {"custom": "field"},
        "http_method": "GET",
    }
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}
    expected_pages = [
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
                http_method="GET",
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
                http_method="GET",
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body={"name": "field"}),
            records=[],
        ),
    ]

    mock_source_adapter_cls = make_mock_adapter_factory(
        iter(
            [
                request_log_message(request),
                response_log_message(response),
                request_log_message(request),
                response_log_message(response),
            ]
        )
    )

    api = DefaultApiImpl(mock_source_adapter_cls, MAX_PAGES_PER_SLICE, MAX_SLICES)

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

    api = DefaultApiImpl(LowCodeSourceAdapterFactory(MAX_PAGES_PER_SLICE, MAX_SLICES), MAX_PAGES_PER_SLICE, MAX_SLICES)
    loop = asyncio.get_event_loop()
    with pytest.raises(HTTPException) as actual_exception:
        loop.run_until_complete(api.read_stream(StreamReadRequestBody(manifest=invalid_manifest, config={}, stream="hashiras")))

    assert actual_exception.value.status_code == expected_status_code


def test_read_stream_invalid_group_format():
    response = {"status_code": 200, "headers": {"field": "value"}, "body": '{"name": "field"}'}

    mock_source_adapter_cls = make_mock_adapter_factory(
        iter(
            [
                response_log_message(response),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
            ]
        )
    )

    api = DefaultApiImpl(mock_source_adapter_cls, MAX_PAGES_PER_SLICE, MAX_SLICES)

    loop = asyncio.get_event_loop()
    with pytest.raises(HTTPException) as actual_exception:
        loop.run_until_complete(api.read_stream(StreamReadRequestBody(manifest=MANIFEST, config=CONFIG, stream="hashiras")))

    assert actual_exception.value.status_code == 400


def test_read_stream_returns_error_if_stream_does_not_exist():
    expected_status_code = 400

    api = DefaultApiImpl(LowCodeSourceAdapterFactory(MAX_PAGES_PER_SLICE, MAX_SLICES), MAX_PAGES_PER_SLICE, MAX_SLICES)
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
                url="https://nichirin.com/v1/swords",
                parameters={"color": ["orange"]},
                headers={"field": "name"},
                body={"key": "value"},
                http_method="PUT",
            ),
            id="test_create_request_with_all_fields",
        ),
        pytest.param(
            'request:{"url": "https://nichirin.com/v1/swords?color=orange", "http_method": "GET", "headers": {"field": "name"}}',
            HttpRequest(
                url="https://nichirin.com/v1/swords", parameters={"color": ["orange"]}, headers={"field": "name"}, http_method="GET"
            ),
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
        pytest.param(
            'request:{"url": "https://nichirin.com/v1/swords", "http_method": "POST", "headers": {"field": "name"}, "body":null}',
            HttpRequest(url="https://nichirin.com/v1/swords", headers={"field": "name"}, body=None, http_method="POST"),
            id="test_create_request_with_null_body",
        ),
        pytest.param("request:{invalid_json: }", None, id="test_invalid_json_still_does_not_crash"),
        pytest.param("just a regular log message", None, id="test_no_request:_prefix_does_not_crash"),
    ],
)
def test_create_request_from_log_message(log_message, expected_request):
    airbyte_log_message = AirbyteLogMessage(level=Level.INFO, message=log_message)
    api = DefaultApiImpl(LowCodeSourceAdapterFactory(MAX_PAGES_PER_SLICE, MAX_SLICES), MAX_PAGES_PER_SLICE, MAX_SLICES)
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
    api = DefaultApiImpl(LowCodeSourceAdapterFactory(MAX_PAGES_PER_SLICE, MAX_SLICES), MAX_PAGES_PER_SLICE, MAX_SLICES)
    actual_response = api._create_response_from_log_message(airbyte_log_message)

    assert actual_response == expected_response


def test_read_stream_with_many_slices():
    request = {}
    response = {"status_code": 200}

    mock_source_adapter_cls = make_mock_adapter_factory(
        iter(
            [
                slice_message(),
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Muichiro Tokito"}),
                slice_message(),
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Shinobu Kocho"}),
                record_message("hashiras", {"name": "Mitsuri Kanroji"}),
                request_log_message(request),
                response_log_message(response),
                record_message("hashiras", {"name": "Obanai Iguro"}),
                request_log_message(request),
                response_log_message(response),
            ]
        )
    )

    api = DefaultApiImpl(mock_source_adapter_cls, MAX_PAGES_PER_SLICE, MAX_SLICES)

    loop = asyncio.get_event_loop()
    stream_read: StreamRead = loop.run_until_complete(
        api.read_stream(StreamReadRequestBody(manifest=MANIFEST, config=CONFIG, stream="hashiras"))
    )

    assert not stream_read.test_read_limit_reached
    assert len(stream_read.slices) == 2

    assert len(stream_read.slices[0].pages) == 1
    assert len(stream_read.slices[0].pages[0].records) == 1

    assert len(stream_read.slices[1].pages) == 3
    assert len(stream_read.slices[1].pages[0].records) == 2
    assert len(stream_read.slices[1].pages[1].records) == 1
    assert len(stream_read.slices[1].pages[2].records) == 0



def test_read_stream_given_maximum_number_of_slices_then_test_read_limit_reached():
    maximum_number_of_slices = 5
    request = {}
    response = {"status_code": 200}
    mock_source_adapter_cls = make_mock_adapter_factory(
        iter(
            [
                slice_message(),
                request_log_message(request),
                response_log_message(response)
            ] * maximum_number_of_slices
        )
    )

    api = DefaultApiImpl(mock_source_adapter_cls, MAX_PAGES_PER_SLICE, MAX_SLICES)

    loop = asyncio.get_event_loop()
    stream_read: StreamRead = loop.run_until_complete(
        api.read_stream(StreamReadRequestBody(manifest=MANIFEST, config=CONFIG, stream="hashiras"))
    )

    assert stream_read.test_read_limit_reached


def test_read_stream_given_maximum_number_of_pages_then_test_read_limit_reached():
    maximum_number_of_pages_per_slice = 5
    request = {}
    response = {"status_code": 200}
    mock_source_adapter_cls = make_mock_adapter_factory(
        iter(
            [slice_message()] + [request_log_message(request), response_log_message(response)] * maximum_number_of_pages_per_slice
        )
    )

    api = DefaultApiImpl(mock_source_adapter_cls, MAX_PAGES_PER_SLICE, MAX_SLICES)

    loop = asyncio.get_event_loop()
    stream_read: StreamRead = loop.run_until_complete(
        api.read_stream(StreamReadRequestBody(manifest=MANIFEST, config=CONFIG, stream="hashiras"))
    )

    assert stream_read.test_read_limit_reached


def test_resolve_manifest():
    _stream_name = "stream_with_custom_requester"
    _stream_primary_key = "id"
    _stream_url_base = "https://api.sendgrid.com"
    _stream_options = {"name": _stream_name, "primary_key": _stream_primary_key, "url_base": _stream_url_base}

    manifest = {
        "version": "version",
        "definitions": {
            "schema_loader": {"name": "{{ options.stream_name }}", "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml"},
            "retriever": {
                "paginator": {
                    "type": "DefaultPaginator",
                    "page_size": 10,
                    "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                    "page_token_option": {"inject_into": "path"},
                    "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                },
                "requester": {
                    "path": "/v3/marketing/lists",
                    "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                    "request_parameters": {"page_size": 10},
                },
                "record_selector": {"extractor": {"field_pointer": ["result"]}},
            },
        },
        "streams": [
            {
                "type": "DeclarativeStream",
                "$options": _stream_options,
                "schema_loader": {"$ref": "*ref(definitions.schema_loader)"},
                "retriever": "*ref(definitions.retriever)",
            },
        ],
        "check": {"type": "CheckStream", "stream_names": ["lists"]},
    }

    expected_resolved_manifest = {
        "type": "DeclarativeSource",
        "version": "version",
        "definitions": {
            "schema_loader": {"name": "{{ options.stream_name }}", "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml"},
            "retriever": {
                "paginator": {
                    "type": "DefaultPaginator",
                    "page_size": 10,
                    "page_size_option": {"inject_into": "request_parameter", "field_name": "page_size"},
                    "page_token_option": {"inject_into": "path"},
                    "pagination_strategy": {"type": "CursorPagination", "cursor_value": "{{ response._metadata.next }}"},
                },
                "requester": {
                    "path": "/v3/marketing/lists",
                    "authenticator": {"type": "BearerAuthenticator", "api_token": "{{ config.apikey }}"},
                    "request_parameters": {"page_size": 10},
                },
                "record_selector": {"extractor": {"field_pointer": ["result"]}},
            },
        },
        "streams": [
            {
                "type": "DeclarativeStream",
                "schema_loader": {
                    "type": "JsonFileSchemaLoader",
                    "name": "{{ options.stream_name }}",
                    "file_path": "./source_sendgrid/schemas/{{ options.name }}.yaml",
                    "primary_key": _stream_primary_key,
                    "url_base": _stream_url_base,
                    "$options": _stream_options,
                },
                "retriever": {
                    "type": "SimpleRetriever",
                    "paginator": {
                        "type": "DefaultPaginator",
                        "page_size": 10,
                        "page_size_option": {
                            "type": "RequestOption",
                            "inject_into": "request_parameter",
                            "field_name": "page_size",
                            "name": _stream_name,
                            "primary_key": _stream_primary_key,
                            "url_base": _stream_url_base,
                            "$options": _stream_options,
                        },
                        "page_token_option": {
                            "type": "RequestOption",
                            "inject_into": "path",
                            "name": _stream_name,
                            "primary_key": _stream_primary_key,
                            "url_base": _stream_url_base,
                            "$options": _stream_options,
                        },
                        "pagination_strategy": {
                            "type": "CursorPagination",
                            "cursor_value": "{{ response._metadata.next }}",
                            "name": _stream_name,
                            "primary_key": _stream_primary_key,
                            "url_base": _stream_url_base,
                            "$options": _stream_options,
                        },
                        "name": _stream_name,
                        "primary_key": _stream_primary_key,
                        "url_base": _stream_url_base,
                        "$options": _stream_options,
                    },
                    "requester": {
                        "type": "HttpRequester",
                        "path": "/v3/marketing/lists",
                        "authenticator": {
                            "type": "BearerAuthenticator",
                            "api_token": "{{ config.apikey }}",
                            "name": _stream_name,
                            "primary_key": _stream_primary_key,
                            "url_base": _stream_url_base,
                            "$options": _stream_options,
                        },
                        "request_parameters": {"page_size": 10},
                        "name": _stream_name,
                        "primary_key": _stream_primary_key,
                        "url_base": _stream_url_base,
                        "$options": _stream_options,
                    },
                    "record_selector": {
                        "type": "RecordSelector",
                        "extractor": {
                            "type": "DpathExtractor",
                            "field_pointer": ["result"],
                            "name": _stream_name,
                            "primary_key": _stream_primary_key,
                            "url_base": _stream_url_base,
                            "$options": _stream_options,
                        },
                        "name": _stream_name,
                        "primary_key": _stream_primary_key,
                        "url_base": _stream_url_base,
                        "$options": _stream_options,
                    },
                    "name": _stream_name,
                    "primary_key": _stream_primary_key,
                    "url_base": _stream_url_base,
                    "$options": _stream_options,
                },
                "name": _stream_name,
                "primary_key": _stream_primary_key,
                "url_base": _stream_url_base,
                "$options": _stream_options,
            },
        ],
        "check": {"type": "CheckStream", "stream_names": ["lists"]},
    }

    api = DefaultApiImpl(LowCodeSourceAdapterFactory(MAX_PAGES_PER_SLICE, MAX_SLICES), MAX_PAGES_PER_SLICE, MAX_SLICES)

    loop = asyncio.get_event_loop()
    actual_response: ResolveManifest = loop.run_until_complete(api.resolve_manifest(ResolveManifestRequestBody(manifest=manifest)))
    assert actual_response.manifest == expected_resolved_manifest


def test_resolve_manifest_unresolvable_references():
    expected_status_code = 400

    invalid_manifest = {
        "version": "version",
        "definitions": {},
        "streams": [
            {"type": "DeclarativeStream", "retriever": "*ref(definitions.retriever)"},
        ],
        "check": {"type": "CheckStream", "stream_names": ["lists"]},
    }

    api = DefaultApiImpl(LowCodeSourceAdapterFactory(MAX_PAGES_PER_SLICE, MAX_SLICES), MAX_PAGES_PER_SLICE, MAX_SLICES)
    loop = asyncio.get_event_loop()
    with pytest.raises(HTTPException) as actual_exception:
        loop.run_until_complete(api.resolve_manifest(ResolveManifestRequestBody(manifest=invalid_manifest)))

    assert "Undefined reference *ref(definitions.retriever)" in actual_exception.value.detail
    assert actual_exception.value.status_code == expected_status_code


def test_resolve_manifest_invalid():
    expected_status_code = 400
    invalid_manifest = {"version": "version"}

    api = DefaultApiImpl(LowCodeSourceAdapterFactory(MAX_PAGES_PER_SLICE, MAX_SLICES), MAX_PAGES_PER_SLICE, MAX_SLICES)
    loop = asyncio.get_event_loop()
    with pytest.raises(HTTPException) as actual_exception:
        loop.run_until_complete(api.resolve_manifest(ResolveManifestRequestBody(manifest=invalid_manifest)))

    assert "Could not resolve manifest with error" in actual_exception.value.detail
    assert actual_exception.value.status_code == expected_status_code


def make_mock_adapter_factory(return_value: Iterator) -> MagicMock:
    mock_source_adapter_factory = MagicMock()
    mock_source_adapter = MagicMock()
    mock_source_adapter.read_stream.return_value = return_value
    mock_source_adapter_factory.create.return_value = mock_source_adapter
    return mock_source_adapter_factory
