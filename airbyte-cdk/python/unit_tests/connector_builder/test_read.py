#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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
        StreamReadPages(
            request=HttpRequest(
                url="https://demonslayers.com/api/v1/hashiras",
                parameters={"era": ["taisho"]},
                headers={"Content-Type": "application/json"},
                body={"custom": "field"},
                http_method="GET",
            ),
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
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
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
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
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
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
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
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
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
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
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
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
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
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
            response=HttpResponse(status=200, headers={"field": "value"}, body='{"name": "field"}'),
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
