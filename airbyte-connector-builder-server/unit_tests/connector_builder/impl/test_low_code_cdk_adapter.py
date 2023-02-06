#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, List, Mapping, Optional, Union
from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, AirbyteRecordMessage, Level, Type
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.requesters.paginators import PaginatorTestReadDecorator
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetrieverTestReadDecorator
from airbyte_cdk.sources.declarative.parsers.custom_exceptions import UndefinedReferenceException
from airbyte_cdk.sources.streams.http import HttpStream

from connector_builder.impl.low_code_cdk_adapter import LowCodeSourceAdapter


class MockConcreteStream(HttpStream, ABC):
    """
    Test class used to verify errors are correctly thrown when the adapter receives unexpected outputs
    """

    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return None

    def url_base(self) -> str:
        return ""

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return ""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[str]:
        return None


MANIFEST = {
    "version": "0.1.0",
    "type" : "DeclarativeSource",
    "definitions": {
        "selector": {"extractor": {"field_pointer": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
        "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type" : "DeclarativeSource" },
        "retriever": {
                "type" : "DeclarativeSource",
            "record_selector": {"extractor": {"field_pointer": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
            "paginator": {"type": "NoPagination"},
            "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
        },
        "hashiras_stream": {
            "retriever": {
                "type" : "DeclarativeSource",
                "record_selector": {"extractor": {"field_pointer": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$options": {"name": "hashiras", "path": "/hashiras"},
        },
        "breathing_techniques_stream": {
            "retriever": {
                "type" : "DeclarativeSource",
                "record_selector": {"extractor": {"field_pointer": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$options": {"name": "breathing-techniques", "path": "/breathing_techniques"},
        },
    },
    "streams": [
        {
            "type" : "DeclarativeStream",
            "retriever": {
                "type" : "SimpleRetriever",
                "record_selector": {"extractor": {"field_pointer": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$options": {"name": "hashiras", "path": "/hashiras"},
        },
        {
            "type" : "DeclarativeStream",
            "retriever": {
                "type" : "SimpleRetriever",
                "record_selector": {"extractor": {"field_pointer": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {"type": "NoPagination"},
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$options": {"name": "breathing-techniques", "path": "/breathing_techniques"},
        },
    ],
    "check": {"stream_names": ["hashiras"], "type": "CheckStream"},
}

MANIFEST_WITH_REFERENCES = {
    "version": "0.1.0",
    "type" : "DeclarativeSource",
    "definitions": {
        "selector": {
            "type": "RecordSelector",
            "extractor": {
                "type": "DpathExtractor",
                "field_pointer": []
            }
        },
        "requester": {
            "type": "HttpRequester",
            "url_base": "https://demonslayers.com/api/v1/",
            "http_method": "GET",
            "authenticator": {
                "type": "BearerAuthenticator",
                "api_token": "{{ config['api_key'] }}"
            }
        },
        "retriever": {
            "type": "SimpleRetriever",
            "record_selector": {
                "$ref": "*ref(definitions.selector)"
            },
            "paginator": {
                "type": "NoPagination"
            },
            "requester": {
                "$ref": "*ref(definitions.requester)"
            }
        },
        "base_stream": {
            "type": "DeclarativeStream",
            "retriever": {
                "$ref": "*ref(definitions.retriever)"
            }
        },
        "ranks_stream": {
            "$ref": "*ref(definitions.base_stream)",
            "$options": {
                "name": "ranks",
                "primary_key": "id",
                "path": "/ranks"
            }
        }
    },
    "streams": ["*ref(definitions.ranks_stream)"],
    "check": {
        "type": "CheckStream",
        "stream_names": ["ranks"]
    },
    "spec": {
        "type": "Spec",
        "documentation_url": "https://docsurl.com",
        "connection_specification": {
            "title": "Source Name Spec",
            "type": "object",
            "required": ["api_key"],
            "additionalProperties": True,
            "properties": {
                "api_key": {
                    "type": "string",
                    "description": "API Key"
                }
            }
        }
    }
}

MANIFEST_WITH_PAGINATOR = {
    "version": "0.1.0",
    "type" : "DeclarativeSource",
    "definitions": {
    },
    "streams": [
        {
            "type" : "DeclarativeStream",
            "retriever": {
                "type" : "SimpleRetriever",
                "record_selector": {"extractor": {"field_pointer": ["items"], "type": "DpathExtractor"}, "type": "RecordSelector"},
                "paginator": {
                    "type": "DefaultPaginator",
                    "pagination_strategy": {
                        "type": "OffsetIncrement",
                        "page_size": 10
                    },
                    "url_base": "https://demonslayers.com/api/v1/"
                },
                "requester": {"url_base": "https://demonslayers.com/api/v1/", "http_method": "GET", "type": "HttpRequester"},
            },
            "$options": {"name": "hashiras", "path": "/hashiras"},
        },
    ],
    "check": {"stream_names": ["hashiras"], "type": "CheckStream"},
}

def test_get_http_streams():
    expected_urls = {"https://demonslayers.com/api/v1/breathing_techniques", "https://demonslayers.com/api/v1/hashiras"}

    adapter = LowCodeSourceAdapter(MANIFEST, MAXIMUM_NUMBER_OF_PAGES_PER_SLICE, MAXIMUM_NUMBER_OF_SLICES)
    actual_streams = adapter.get_http_streams(config={})
    actual_urls = {http_stream.url_base + http_stream.path() for http_stream in actual_streams}

    assert len(actual_streams) == len(expected_urls)
    assert actual_urls == expected_urls


MAXIMUM_NUMBER_OF_PAGES_PER_SLICE = 5
MAXIMUM_NUMBER_OF_SLICES = 5

def test_get_http_manifest_with_references():
    expected_urls = {"https://demonslayers.com/api/v1/ranks"}

    adapter = LowCodeSourceAdapter(MANIFEST_WITH_REFERENCES, MAXIMUM_NUMBER_OF_PAGES_PER_SLICE, MAXIMUM_NUMBER_OF_SLICES)
    actual_streams = adapter.get_http_streams(config={})
    actual_urls = {http_stream.url_base + http_stream.path() for http_stream in actual_streams}

    assert len(actual_streams) == len(expected_urls)
    assert actual_urls == expected_urls


def test_get_http_streams_non_declarative_streams():
    non_declarative_stream = MockConcreteStream()

    mock_source = MagicMock()
    mock_source.streams.return_value = [non_declarative_stream]

    adapter = LowCodeSourceAdapter(MANIFEST, MAXIMUM_NUMBER_OF_PAGES_PER_SLICE, MAXIMUM_NUMBER_OF_SLICES)
    adapter._source = mock_source
    with pytest.raises(TypeError):
        adapter.get_http_streams(config={})


def test_get_http_streams_non_http_stream():
    declarative_stream_non_http_retriever = DeclarativeStream(name="hashiras", primary_key="id", retriever=MagicMock(), config={},
                                                              options={})

    mock_source = MagicMock()
    mock_source.streams.return_value = [declarative_stream_non_http_retriever]

    adapter = LowCodeSourceAdapter(MANIFEST, MAXIMUM_NUMBER_OF_PAGES_PER_SLICE, MAXIMUM_NUMBER_OF_SLICES)
    adapter._source = mock_source
    with pytest.raises(TypeError):
        adapter.get_http_streams(config={})


def test_read_streams():
    expected_messages = iter([
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
    ])
    mock_source = MagicMock()
    mock_source.read.return_value = expected_messages

    adapter = LowCodeSourceAdapter(MANIFEST, MAXIMUM_NUMBER_OF_PAGES_PER_SLICE, MAXIMUM_NUMBER_OF_SLICES)
    adapter._source = mock_source
    actual_messages = list(adapter.read_stream("hashiras", {}))

    for i, expected_message in enumerate(expected_messages):
        assert actual_messages[i] == expected_message


def test_read_streams_with_error():
    expected_messages = [
        AirbyteMessage(
            type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="request:{'url': 'https://demonslayers.com/v1/hashiras'}")
        ),
        AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="response:{'status': 401}")),
        AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.ERROR, message="error_message")),
    ]
    mock_source = MagicMock()

    def return_value(*args, **kwargs):
        yield expected_messages[0]
        yield expected_messages[1]
        raise Exception("error_message")

    mock_source.read.side_effect = return_value

    adapter = LowCodeSourceAdapter(MANIFEST, MAXIMUM_NUMBER_OF_PAGES_PER_SLICE, MAXIMUM_NUMBER_OF_SLICES)
    adapter._source = mock_source
    actual_messages = list(adapter.read_stream("hashiras", {}))

    for i, expected_message in enumerate(expected_messages):
        assert actual_messages[i] == expected_message


def test_read_streams_invalid_reference():
    invalid_reference_manifest = {
        "version": "0.1.0",
        "type" : "DeclarativeSource",
        "definitions": {
            "selector": {
                "type": "RecordSelector",
                "extractor": {
                    "type": "DpathExtractor",
                    "field_pointer": []
                }
            },
            "ranks_stream": {
                "$ref": "*ref(definitions.base_stream)",
                "$options": {
                    "name": "ranks",
                    "primary_key": "id",
                    "path": "/ranks"
                }
            }
        },
        "streams": ["*ref(definitions.ranks_stream)"],
        "check": {
            "type": "CheckStream",
            "stream_names": ["ranks"]
        }
    }

    with pytest.raises(UndefinedReferenceException):
        LowCodeSourceAdapter(invalid_reference_manifest, MAXIMUM_NUMBER_OF_PAGES_PER_SLICE, MAXIMUM_NUMBER_OF_SLICES)


def test_stream_use_read_test_retriever_and_paginator():
    adapter = LowCodeSourceAdapter(MANIFEST_WITH_PAGINATOR, MAXIMUM_NUMBER_OF_PAGES_PER_SLICE, MAXIMUM_NUMBER_OF_SLICES)
    streams = adapter.get_http_streams(config={})

    assert streams
    for stream in streams:
        assert isinstance(stream, SimpleRetrieverTestReadDecorator)
        assert isinstance(stream.paginator, PaginatorTestReadDecorator)
