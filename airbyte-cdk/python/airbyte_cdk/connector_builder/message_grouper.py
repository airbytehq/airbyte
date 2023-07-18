#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from copy import deepcopy
from json import JSONDecodeError
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional, Union
from urllib.parse import parse_qs, urlparse

from airbyte_cdk.connector_builder.models import (
    AuxiliaryRequest,
    HttpRequest,
    HttpResponse,
    LogMessage,
    StreamRead,
    StreamReadPages,
    StreamReadSlices,
)
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.datetime_format_inferrer import DatetimeFormatInferrer
from airbyte_cdk.utils.schema_inferrer import SchemaInferrer
from airbyte_protocol.models.airbyte_protocol import (
    AirbyteControlMessage,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    Level,
    OrchestratorType,
    TraceType,
)
from airbyte_protocol.models.airbyte_protocol import Type as MessageType


class MessageGrouper:
    logger = logging.getLogger("airbyte.connector-builder")

    def __init__(self, max_pages_per_slice: int, max_slices: int, max_record_limit: int = 1000):
        self._max_pages_per_slice = max_pages_per_slice
        self._max_slices = max_slices
        self._max_record_limit = max_record_limit

    def get_message_groups(
        self,
        source: DeclarativeSource,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        record_limit: Optional[int] = None,
    ) -> StreamRead:
        if record_limit is not None and not (1 <= record_limit <= 1000):
            raise ValueError(f"Record limit must be between 1 and 1000. Got {record_limit}")
        schema_inferrer = SchemaInferrer()
        datetime_format_inferrer = DatetimeFormatInferrer()

        if record_limit is None:
            record_limit = self._max_record_limit
        else:
            record_limit = min(record_limit, self._max_record_limit)

        slices = []
        log_messages = []
        latest_config_update: AirbyteControlMessage = None
        auxiliary_requests = []
        for message_group in self._get_message_groups(
                self._read_stream(source, config, configured_catalog),
                schema_inferrer,
                datetime_format_inferrer,
                record_limit,
        ):
            if isinstance(message_group, AirbyteLogMessage):
                log_messages.append(LogMessage(**{"message": message_group.message, "level": message_group.level.value}))
            elif isinstance(message_group, AirbyteTraceMessage):
                if message_group.type == TraceType.ERROR:
                    error_message = f"{message_group.error.message} - {message_group.error.stack_trace}"
                    log_messages.append(LogMessage(**{"message": error_message, "level": "ERROR"}))
            elif isinstance(message_group, AirbyteControlMessage):
                if not latest_config_update or latest_config_update.emitted_at <= message_group.emitted_at:
                    latest_config_update = message_group
            elif isinstance(message_group, AuxiliaryRequest):
                auxiliary_requests.append(message_group)
            else:
                slices.append(message_group)

        return StreamRead(
            logs=log_messages,
            slices=slices,
            test_read_limit_reached=self._has_reached_limit(slices),
            auxiliary_requests=auxiliary_requests,
            inferred_schema=schema_inferrer.get_stream_schema(
                configured_catalog.streams[0].stream.name
            ),  # The connector builder currently only supports reading from a single stream at a time
            latest_config_update=self._clean_config(latest_config_update.connectorConfig.config) if latest_config_update else None,
            inferred_datetime_formats=datetime_format_inferrer.get_inferred_datetime_formats(),
        )

    def _get_message_groups(
            self, messages: Iterator[AirbyteMessage], schema_inferrer: SchemaInferrer, datetime_format_inferrer: DatetimeFormatInferrer, limit: int
    ) -> Iterable[Union[StreamReadPages, AirbyteControlMessage, AirbyteLogMessage, AirbyteTraceMessage, AuxiliaryRequest]]:
        """
        Message groups are partitioned according to when request log messages are received. Subsequent response log messages
        and record messages belong to the prior request log message and when we encounter another request, append the latest
        message group, until <limit> records have been read.

        Messages received from the CDK read operation will always arrive in the following order:
        {type: LOG, log: {message: "request: ..."}}
        {type: LOG, log: {message: "response: ..."}}
        ... 0 or more record messages
        {type: RECORD, record: {data: ...}}
        {type: RECORD, record: {data: ...}}
        Repeats for each request/response made

        Note: The exception is that normal log messages can be received at any time which are not incorporated into grouping
        """
        records_count = 0
        at_least_one_page_in_group = False
        current_page_records = []
        current_slice_descriptor: Dict[str, Any] = None
        current_slice_pages = []
        current_page_request: Optional[HttpRequest] = None
        current_page_response: Optional[HttpResponse] = None
        had_error = False

        while records_count < limit and (message := next(messages, None)):
            json_message = self._parse_json(message.log) if message.type == MessageType.LOG else None
            if self._need_to_close_page(at_least_one_page_in_group, message, json_message):
                self._close_page(current_page_request, current_page_response, current_slice_pages, current_page_records, True)
                current_page_request = None
                current_page_response = None

            if at_least_one_page_in_group and message.type == MessageType.LOG and message.log.message.startswith(AbstractSource.SLICE_LOG_PREFIX):
                yield StreamReadSlices(pages=current_slice_pages, slice_descriptor=current_slice_descriptor)
                current_slice_descriptor = self._parse_slice_description(message.log.message)
                current_slice_pages = []
                at_least_one_page_in_group = False
            elif message.type == MessageType.LOG and message.log.message.startswith(AbstractSource.SLICE_LOG_PREFIX):
                # parsing the first slice
                current_slice_descriptor = self._parse_slice_description(message.log.message)
            elif message.type == MessageType.LOG:
                if self._is_http_log(json_message):
                    if self._is_auxiliary_http_request(json_message):
                        title_prefix = (
                           "Parent stream: " if json_message.get("airbyte_cdk", {}).get("stream", {}).get("is_substream", False) else ""
                        )
                        yield AuxiliaryRequest(
                            title=title_prefix + json_message.get("http", {}).get("title", None),
                            description=json_message.get("http", {}).get("description", None),
                            request=self._create_request_from_log_message(json_message),
                            response=self._create_response_from_log_message(json_message),
                        )
                    else:
                        at_least_one_page_in_group = True
                        current_page_request = self._create_request_from_log_message(json_message)
                        current_page_response = self._create_response_from_log_message(json_message)
                else:
                    if message.log.level == Level.ERROR:
                        had_error = True
                    yield message.log
            elif message.type == MessageType.TRACE:
                if message.trace.type == TraceType.ERROR:
                    had_error = True
                    yield message.trace
            elif message.type == MessageType.RECORD:
                current_page_records.append(message.record.data)
                records_count += 1
                schema_inferrer.accumulate(message.record)
                datetime_format_inferrer.accumulate(message.record)
            elif message.type == MessageType.CONTROL and message.control.type == OrchestratorType.CONNECTOR_CONFIG:
                yield message.control
        else:
            self._close_page(current_page_request, current_page_response, current_slice_pages, current_page_records, validate_page_complete=not had_error)
            yield StreamReadSlices(pages=current_slice_pages, slice_descriptor=current_slice_descriptor)

    @staticmethod
    def _need_to_close_page(at_least_one_page_in_group: bool, message: AirbyteMessage, json_message: Optional[dict]) -> bool:
        return (
            at_least_one_page_in_group
            and message.type == MessageType.LOG
            and (MessageGrouper._is_page_http_request(json_message) or message.log.message.startswith("slice:"))
        )

    @staticmethod
    def _is_page_http_request(json_message):
        return MessageGrouper._is_http_log(json_message) and not MessageGrouper._is_auxiliary_http_request(json_message)

    @staticmethod
    def _is_http_log(message: Optional[dict]) -> bool:
        return message and bool(message.get("http", False))

    @staticmethod
    def _is_auxiliary_http_request(message: Optional[dict]) -> bool:
        """
        A auxiliary request is a request that is performed and will not directly lead to record for the specific stream it is being queried.
        A couple of examples are:
        * OAuth authentication
        * Substream slice generation
        """
        if not message:
            return False

        is_http = MessageGrouper._is_http_log(message)
        return is_http and message.get("http", {}).get("is_auxiliary", False)

    @staticmethod
    def _close_page(current_page_request, current_page_response, current_slice_pages, current_page_records, validate_page_complete: bool):
        """
        Close a page when parsing message groups
        @param validate_page_complete: in some cases, we expect the CDK to not return a response. As of today, this will only happen before
        an uncaught exception and therefore, the assumption is that `validate_page_complete=True` only on the last page that is being closed
        """
        if validate_page_complete and (not current_page_request or not current_page_response):
            raise ValueError("Every message grouping should have at least one request and response")

        current_slice_pages.append(
            StreamReadPages(request=current_page_request, response=current_page_response, records=deepcopy(current_page_records))
        )
        current_page_records.clear()

    def _read_stream(self, source: DeclarativeSource, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog) -> Iterator[AirbyteMessage]:
        # the generator can raise an exception
        # iterate over the generated messages. if next raise an exception, catch it and yield it as an AirbyteLogMessage
        try:
            yield from AirbyteEntrypoint(source).read(source.spec(self.logger), config, configured_catalog, {})
        except Exception as e:
            error_message = f"{e.args[0] if len(e.args) > 0 else str(e)}"
            yield AirbyteTracedException.from_exception(e, message=error_message).as_airbyte_message()

    @staticmethod
    def _parse_json(log_message: AirbyteLogMessage):
        # TODO: As a temporary stopgap, the CDK emits request/response data as a log message string. Ideally this should come in the
        # form of a custom message object defined in the Airbyte protocol, but this unblocks us in the immediate while the
        # protocol change is worked on.
        try:
            return json.loads(log_message.message)
        except JSONDecodeError:
            return None

    @staticmethod
    def _create_request_from_log_message(json_http_message: dict) -> HttpRequest:
        url = urlparse(json_http_message.get("url", {}).get("full", ""))
        full_path = f"{url.scheme}://{url.hostname}{url.path}" if url else ""
        request = json_http_message.get("http", {}).get("request", {})
        parameters = parse_qs(url.query) or None
        return HttpRequest(
            url=full_path,
            http_method=request.get("method", ""),
            headers=request.get("headers"),
            parameters=parameters,
            body=request.get("body", {}).get("content", ""),
        )

    @staticmethod
    def _create_response_from_log_message(json_http_message: dict) -> HttpResponse:
        response = json_http_message.get("http", {}).get("response", {})
        body = response.get("body", {}).get("content", "")
        return HttpResponse(status=response.get("status_code"), body=body, headers=response.get("headers"))

    def _has_reached_limit(self, slices: List[StreamReadPages]):
        if len(slices) >= self._max_slices:
            return True

        for slice in slices:
            if len(slice.pages) >= self._max_pages_per_slice:
                return True
        return False

    def _parse_slice_description(self, log_message):
        return json.loads(log_message.replace(AbstractSource.SLICE_LOG_PREFIX, "", 1))

    @staticmethod
    def _clean_config(config: Mapping[str, Any]):
        cleaned_config = deepcopy(config)
        for key in config.keys():
            if key.startswith("__"):
                del cleaned_config[key]
        return cleaned_config
