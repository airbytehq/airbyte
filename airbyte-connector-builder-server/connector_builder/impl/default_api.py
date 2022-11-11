#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import logging
from json import JSONDecodeError
from typing import List, Optional
from urllib.parse import parse_qs, urljoin, urlparse

from airbyte_cdk.models import AirbyteLogMessage, Type
from connector_builder.generated.apis.default_api_interface import DefaultApi
from connector_builder.generated.models.http_request import HttpRequest
from connector_builder.generated.models.http_response import HttpResponse
from connector_builder.generated.models.known_exception_info import KnownExceptionInfo
from connector_builder.generated.models.stream_read import StreamRead
from connector_builder.generated.models.stream_read_pages import StreamReadPages
from connector_builder.generated.models.stream_read_request_body import StreamReadRequestBody
from connector_builder.generated.models.stream_read_slices import StreamReadSlices
from connector_builder.generated.models.streams_list_read import StreamsListRead
from connector_builder.generated.models.streams_list_read_streams import StreamsListReadStreams
from connector_builder.generated.models.streams_list_request_body import StreamsListRequestBody
from connector_builder.impl.low_code_cdk_adapter import LowCodeSourceAdapter
from fastapi import Body
from jsonschema import ValidationError


class DefaultApiImpl(DefaultApi):
    def __init__(self):
        self.logger = logging.getLogger("airbyte.connector-builder")

    async def get_manifest_template(self) -> str:
        return "Hello World"

    async def list_streams(self, streams_list_request_body: StreamsListRequestBody = Body(None, description="")) -> StreamsListRead:
        """
        Takes in a low code manifest and a config to resolve the list of streams that are available for testing
        :param streams_list_request_body: Input parameters to retrieve the list of available streams
        :return: Stream objects made up of a stream name and the HTTP URL it will send requests to
        """
        adapter = LowCodeSourceAdapter(streams_list_request_body.manifest)

        stream_list_read = []
        for http_stream in adapter.get_http_streams(streams_list_request_body.config):
            stream_list_read.append(
                StreamsListReadStreams(
                    name=http_stream.name,
                    url=urljoin(http_stream.url_base, http_stream.path()),
                )
            )
        return StreamsListRead(streams=stream_list_read)

    async def read_stream(self, stream_read_request_body: StreamReadRequestBody = Body(None, description="")) -> StreamRead:
        """
        Using the provided manifest and config, invokes a sync for the specified stream and returns groups of Airbyte messages
        that are produced during the read operation
        :param stream_read_request_body: Input parameters to trigger the read operation for a stream
        :return: Airbyte record messages produced by the sync grouped by slice and page
        """
        return self.temp_read_stream(stream_read_request_body)

    def temp_read_stream(self, stream_read_request_body: StreamReadRequestBody = Body(None, description="")) -> StreamRead:
        try:
            adapter = self._create_low_code_adapter(stream_read_request_body)
        except ValidationError as error:
            return KnownExceptionInfo(
                message=f"Invalid connector manifest with error: {error.message}", exception_class_name=ValidationError.__name__
            )

        single_slice = StreamReadSlices(pages=[])
        log_messages = []

        first_page = True
        current_records: List[object] = []
        current_page_request: Optional[HttpRequest] = None
        current_page_response: Optional[HttpResponse] = None
        try:
            # Message groups are partitioned according to when request log messages are received. Subsequent response log messages
            # and record messages belong to the prior request log message and when we encounter another request, append the latest
            # message group
            for message in adapter.read_stream(stream_read_request_body.stream, stream_read_request_body.config):
                if first_page and message.type == Type.LOG and message.log.message.startswith("request:"):
                    first_page = False
                    request = self._create_request_from_log_message(message.log)
                    current_page_request = request
                elif message.type == Type.LOG and message.log.message.startswith("request:"):
                    if not current_page_request or not current_page_response:
                        self.logger.warning("Every message grouping should have at least one request and response")
                    single_slice.pages.append(
                        StreamReadPages(request=current_page_request, response=current_page_response, records=current_records)
                    )
                    current_page_request = self._create_request_from_log_message(message.log)
                    current_records = []
                elif message.type == Type.LOG and message.log.message.startswith("response:"):
                    current_page_response = self._create_response_from_log_message(message.log)
                elif message.type == Type.LOG:
                    log_messages.append({"message": message.log.message})
                elif message.type == Type.RECORD:
                    current_records.append(message.record.data)
            else:
                if not current_page_request or not current_page_response:
                    self.logger.warning("Every message grouping should have at least one request and response")
                single_slice.pages.append(
                    StreamReadPages(request=current_page_request, response=current_page_response, records=current_records)
                )
        except KeyError as error:
            return KnownExceptionInfo(message=error.args[0])

        return StreamRead(logs=log_messages, slices=[single_slice])

    def _create_request_from_log_message(self, log_message: AirbyteLogMessage) -> Optional[HttpRequest]:
        raw_request = log_message.message.partition("request:")[2]
        try:
            request = json.loads(raw_request)
            url = urlparse(request.get("url", ""))
            full_path = f"{url.scheme}://{url.hostname}{url.path}" if url else ""
            parameters = parse_qs(url.query) or None
            return HttpRequest(url=full_path, headers=request.get("headers"), parameters=parameters, body=request.get("body"))
        except JSONDecodeError as error:
            self.logger.warning(f"Failed to parse log message into request object with error: {error}")
            return None

    def _create_response_from_log_message(self, log_message: AirbyteLogMessage) -> Optional[HttpResponse]:
        raw_response = log_message.message.partition("response:")[2]
        try:
            response = json.loads(raw_response)
            body = json.loads(response.get("body", "{}"))
            return HttpResponse(status=response.get("status_code"), body=body, headers=response.get("headers"))
        except JSONDecodeError as error:
            self.logger.warning(f"Failed to parse log message into response object with error: {error}")
            return None

    @staticmethod
    def _create_low_code_adapter(stream_read_request_body: StreamReadRequestBody) -> LowCodeSourceAdapter:
        return LowCodeSourceAdapter(stream_read_request_body.manifest)


WIKI_MANIFEST = {
    "version": "0.1.0",
    "definitions": {
        "selector": {"extractor": {"field_pointer": ["items"]}},
        "requester": {
            "url_base": "https://wikimedia.org/api/rest_v1/metrics/pageviews",
            "http_method": "GET",
            "request_options_provider": {
                "request_headers": {"User-Agent": "AirbyteWikipediaPageviewsConnector/1.0 (https://github.com/airbytehq/airbyte)"}
            },
        },
        "top_stream_slicer": {
            "type": "DatetimeStreamSlicer",
            "start_datetime": {"datetime": "{{config.start}}", "datetime_format": "%Y%m%d"},
            "end_datetime": {"datetime": "{{config.start}}", "datetime_format": "%Y%m%d"},
            "step": "1d",
            "cursor_field": "timestamp",
            "datetime_format": "%Y/%m/%d",
        },
        "per_article_stream_slicer": {
            "type": "DatetimeStreamSlicer",
            "start_datetime": "{{config.start}}",
            "end_datetime": "{{config.end}}",
            "step": "1d",
            "cursor_field": "timestamp",
            "datetime_format": "%Y%m%d",
        },
        "per_article_requester": {
            "$options": {
                "url_base": "https://wikimedia.org/api/rest_v1/metrics/pageviews",
                "http_method": "GET",
                "request_options_provider": {
                    "request_headers": {"User-Agent": "AirbyteWikipediaPageviewsConnector/1.0 (https://github.com/airbytehq/airbyte)"}
                },
            },
            "path": "/per-article/{{config.project}}/{{config.access}}/{{config.agent}}/{{config.article}}/daily/{{stream_slice.start_time}}/{{stream_slice.end_time}}",
        },
        "top_requester": {
            "$options": {
                "url_base": "https://wikimedia.org/api/rest_v1/metrics/pageviews",
                "http_method": "GET",
                "request_options_provider": {
                    "request_headers": {"User-Agent": "AirbyteWikipediaPageviewsConnector/1.0 (https://github.com/airbytehq/airbyte)"}
                },
            },
            "path": "/top/{{config.project}}/{{config.access}}/{{stream_slice.start_time}}",
        },
        "per_article_retriever": {
            "record_selector": {"extractor": {"field_pointer": ["items"]}},
            "paginator": {"type": "NoPagination"},
            "requester": {
                "$options": {
                    "url_base": "https://wikimedia.org/api/rest_v1/metrics/pageviews",
                    "http_method": "GET",
                    "request_options_provider": {
                        "request_headers": {"User-Agent": "AirbyteWikipediaPageviewsConnector/1.0 (https://github.com/airbytehq/airbyte)"}
                    },
                },
                "path": "/per-article/{{config.project}}/{{config.access}}/{{config.agent}}/{{config.article}}/daily/{{stream_slice.start_time}}/{{stream_slice.end_time}}",
            },
            "stream_slicer": {
                "type": "DatetimeStreamSlicer",
                "start_datetime": "{{config.start}}",
                "end_datetime": "{{config.end}}",
                "step": "1d",
                "cursor_field": "timestamp",
                "datetime_format": "%Y%m%d",
            },
        },
        "top_retriever": {
            "record_selector": {"extractor": {"field_pointer": ["items"]}},
            "paginator": {"type": "NoPagination"},
            "requester": {
                "$options": {
                    "url_base": "https://wikimedia.org/api/rest_v1/metrics/pageviews",
                    "http_method": "GET",
                    "request_options_provider": {
                        "request_headers": {"User-Agent": "AirbyteWikipediaPageviewsConnector/1.0 (https://github.com/airbytehq/airbyte)"}
                    },
                },
                "path": "/top/{{config.project}}/{{config.access}}/{{stream_slice.start_time}}",
            },
            "stream_slicer": {
                "type": "DatetimeStreamSlicer",
                "start_datetime": {"datetime": "{{config.start}}", "datetime_format": "%Y%m%d"},
                "end_datetime": {"datetime": "{{config.start}}", "datetime_format": "%Y%m%d"},
                "step": "1d",
                "cursor_field": "timestamp",
                "datetime_format": "%Y/%m/%d",
            },
        },
        "per_article_stream": {
            "retriever": {
                "record_selector": {"extractor": {"field_pointer": ["items"]}},
                "paginator": {"type": "NoPagination"},
                "requester": {
                    "$options": {
                        "url_base": "https://wikimedia.org/api/rest_v1/metrics/pageviews",
                        "http_method": "GET",
                        "request_options_provider": {
                            "request_headers": {
                                "User-Agent": "AirbyteWikipediaPageviewsConnector/1.0 (https://github.com/airbytehq/airbyte)"
                            }
                        },
                    },
                    "path": "/per-article/{{config.project}}/{{config.access}}/{{config.agent}}/{{config.article}}/daily/{{stream_slice.start_time}}/{{stream_slice.end_time}}",
                },
                "stream_slicer": {
                    "type": "DatetimeStreamSlicer",
                    "start_datetime": "{{config.start}}",
                    "end_datetime": "{{config.end}}",
                    "step": "1d",
                    "cursor_field": "timestamp",
                    "datetime_format": "%Y%m%d",
                },
            },
            "$options": {"name": "per-article"},
            "class_name": "airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream",
        },
        "top_stream": {
            "retriever": {
                "record_selector": {"extractor": {"field_pointer": ["items"]}},
                "paginator": {"type": "NoPagination"},
                "requester": {
                    "$options": {
                        "url_base": "https://wikimedia.org/api/rest_v1/metrics/pageviews",
                        "http_method": "GET",
                        "request_options_provider": {
                            "request_headers": {
                                "User-Agent": "AirbyteWikipediaPageviewsConnector/1.0 (https://github.com/airbytehq/airbyte)"
                            }
                        },
                    },
                    "path": "/top/{{config.project}}/{{config.access}}/{{stream_slice.start_time}}",
                },
                "stream_slicer": {
                    "type": "DatetimeStreamSlicer",
                    "start_datetime": {"datetime": "{{config.start}}", "datetime_format": "%Y%m%d"},
                    "end_datetime": {"datetime": "{{config.start}}", "datetime_format": "%Y%m%d"},
                    "step": "1d",
                    "cursor_field": "timestamp",
                    "datetime_format": "%Y/%m/%d",
                },
            },
            "$options": {"name": "top"},
            "class_name": "airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream",
        },
    },
    "streams": [
        {
            "retriever": {
                "record_selector": {"extractor": {"field_pointer": ["items"]}},
                "paginator": {"type": "NoPagination"},
                "requester": {
                    "$options": {
                        "url_base": "https://wikimedia.org/api/rest_v1/metrics/pageviews",
                        "http_method": "GET",
                        "request_options_provider": {
                            "request_headers": {
                                "User-Agent": "AirbyteWikipediaPageviewsConnector/1.0 (https://github.com/airbytehq/airbyte)"
                            }
                        },
                    },
                    "path": "/per-article/{{config.project}}/{{config.access}}/{{config.agent}}/{{config.article}}/daily/{{stream_slice.start_time}}/{{stream_slice.end_time}}",
                },
                "stream_slicer": {
                    "type": "DatetimeStreamSlicer",
                    "start_datetime": "{{config.start}}",
                    "end_datetime": "{{config.end}}",
                    "step": "1d",
                    "cursor_field": "timestamp",
                    "datetime_format": "%Y%m%d",
                },
            },
            "$options": {"name": "per-article"},
            "class_name": "airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream",
        },
        {
            "retriever": {
                "record_selector": {"extractor": {"field_pointer": ["items"]}},
                "paginator": {"type": "NoPagination"},
                "requester": {
                    "$options": {
                        "url_base": "https://wikimedia.org/api/rest_v1/metrics/pageviews",
                        "http_method": "GET",
                        "request_options_provider": {
                            "request_headers": {
                                "User-Agent": "AirbyteWikipediaPageviewsConnector/1.0 (https://github.com/airbytehq/airbyte)"
                            }
                        },
                    },
                    "path": "/top/{{config.project}}/{{config.access}}/{{stream_slice.start_time}}",
                },
                "stream_slicer": {
                    "type": "DatetimeStreamSlicer",
                    "start_datetime": {"datetime": "{{config.start}}", "datetime_format": "%Y%m%d"},
                    "end_datetime": {"datetime": "{{config.start}}", "datetime_format": "%Y%m%d"},
                    "step": "1d",
                    "cursor_field": "timestamp",
                    "datetime_format": "%Y/%m/%d",
                },
            },
            "$options": {"name": "top"},
            "class_name": "airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream",
        },
    ],
    "check": {"stream_names": ["per-article", "top"], "class_name": "airbyte_cdk.sources.declarative.checks.check_stream.CheckStream"},
}
