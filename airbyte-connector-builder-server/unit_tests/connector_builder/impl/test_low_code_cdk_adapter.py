#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, AirbyteRecordMessage, Level, Type
from connector_builder.impl.low_code_cdk_adapter import LowCodeSourceAdapter

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
INVALID_MANIFEST = {
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


def test_get_http_streams():
    expected_urls = {"https://demonslayers.com/api/v1/breathing_techniques", "https://demonslayers.com/api/v1/hashiras"}
    # manifest["definitions"]["requester"]["url_base"] = 'https://demonslayers.com/api/{{ config.api_version }}/'

    adapter = LowCodeSourceAdapter(MANIFEST)
    actual_streams = adapter.get_http_streams(config={})
    actual_urls = {http_stream.url_base + http_stream.path() for http_stream in actual_streams}

    assert len(actual_streams) == len(expected_urls)
    assert actual_urls == expected_urls


def test_read_streams():
    expected_messages = [
        AirbyteMessage(
            type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="request:{'url': 'https://demonslayers.com/v1/hashiras'}")
        ),
        AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="response:{'status': 200}")),
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(data={"name": "Tengen Uzui", "breathing_technique": "sound"}, emitted_at=1234, stream="hashiras"),
        ),
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                data={"name": "Kyojuro Rengoku", "breathing_technique": "fire"}, emitted_at=1234, stream="hashiras"
            ),
        ),
        AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(data={"name": "Giyu Tomioka", "breathing_technique": "water"}, emitted_at=1234, stream="hashiras"),
        ),
    ]
    mock_source = MagicMock()
    mock_source.read.returns = expected_messages

    adapter = LowCodeSourceAdapter(MANIFEST)
    adapter._source = mock_source
    actual_messages = adapter.read_stream("hashiras", {})

    for i, actual_message in enumerate(actual_messages):
        assert actual_message == expected_messages[i]
