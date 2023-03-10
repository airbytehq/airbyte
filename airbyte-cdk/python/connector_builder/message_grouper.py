#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from json import JSONDecodeError
from typing import Any, Iterable, Iterator, Mapping, Optional, Union
from urllib.parse import parse_qs, urlparse

from airbyte_protocol.models.airbyte_protocol import ConfiguredAirbyteCatalog

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Type
from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.utils.schema_inferrer import SchemaInferrer
from connector_builder.models import StreamRead, StreamReadPages, HttpResponse, HttpRequest, StreamReadSlices
import logging
from copy import deepcopy


class MessageGrouper:
    logger = logging.getLogger("airbyte.connector-builder")

    def __init__(self, max_pages_per_slice: int, max_slices: int, max_record_limit: int = 1000):
        self._max_pages_per_slice = max_pages_per_slice
        self._max_slices = max_slices
        self.max_record_limit = max_record_limit

    def get_grouped_messages(self,
                             source: DeclarativeSource,
                             config: Mapping[str, Any],
                             stream: str,
                             record_limit: Optional[int] = None,
    ) -> StreamRead:
        if record_limit is not None and not (1 <= record_limit <= 1000):
            raise ValueError(f"Record limit must be between 1 and 1000. Got {record_limit}")
        schema_inferrer = SchemaInferrer()

        if record_limit is None:
            record_limit = self.max_record_limit
        else:
            record_limit = min(record_limit, self.max_record_limit)

        slices = []
        log_messages = []
        state = {} # No support for incremental sync
        catalog = MessageGrouper._create_configure_catalog(stream)
        for message_group in self._get_message_groups(
                source.read(self.logger, config, catalog, state),
                schema_inferrer,
                record_limit,
        ):
            if isinstance(message_group, AirbyteLogMessage):
                log_messages.append({"message": message_group.message})
            else:
                slices.append(message_group)

        return StreamRead(
            logs=log_messages,
            slices=slices,
            test_read_limit_reached=self._has_reached_limit(slices),
            inferred_schema=schema_inferrer.get_stream_schema(stream)
        )

    def _get_message_groups(
            self, messages: Iterator[AirbyteMessage], schema_inferrer: SchemaInferrer, limit: int
    ) -> Iterable[Union[StreamReadPages, AirbyteLogMessage]]:
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
        current_slice_pages = []
        current_page_request: Optional[HttpRequest] = None
        current_page_response: Optional[HttpResponse] = None

        while records_count < limit and (message := next(messages, None)):
            if self._need_to_close_page(at_least_one_page_in_group, message):
                self._close_page(current_page_request, current_page_response, current_slice_pages, current_page_records)
                current_page_request = None
                current_page_response = None

            if at_least_one_page_in_group and message.type == Type.LOG and message.log.message.startswith("slice:"):
                yield StreamReadSlices(pages=current_slice_pages)
                current_slice_pages = []
                at_least_one_page_in_group = False
            elif message.type == Type.LOG and message.log.message.startswith("request:"):
                if not at_least_one_page_in_group:
                    at_least_one_page_in_group = True
                current_page_request = self._create_request_from_log_message(message.log)
            elif message.type == Type.LOG and message.log.message.startswith("response:"):
                current_page_response = self._create_response_from_log_message(message.log)
            elif message.type == Type.LOG:
                yield message.log
            elif message.type == Type.RECORD:
                current_page_records.append(message.record.data)
                records_count += 1
                schema_inferrer.accumulate(message.record)
        else:
            self._close_page(current_page_request, current_page_response, current_slice_pages, current_page_records)
            yield StreamReadSlices(pages=current_slice_pages)

    @staticmethod
    def _need_to_close_page(at_least_one_page_in_group, message):
        return (
                at_least_one_page_in_group
                and message.type == Type.LOG
                and (message.log.message.startswith("request:") or message.log.message.startswith("slice:"))
        )

    @staticmethod
    def _close_page(current_page_request, current_page_response, current_slice_pages, current_page_records):
        if not current_page_request or not current_page_response:
            raise ValueError("Every message grouping should have at least one request and response")

        current_slice_pages.append(
            StreamReadPages(request=current_page_request, response=current_page_response, records=deepcopy(current_page_records))
        )
        current_page_records.clear()

    def _create_request_from_log_message(self, log_message: AirbyteLogMessage) -> Optional[HttpRequest]:
        # TODO: As a temporary stopgap, the CDK emits request data as a log message string. Ideally this should come in the
        # form of a custom message object defined in the Airbyte protocol, but this unblocks us in the immediate while the
        # protocol change is worked on.
        raw_request = log_message.message.partition("request:")[2]
        try:
            request = json.loads(raw_request)
            url = urlparse(request.get("url", ""))
            full_path = f"{url.scheme}://{url.hostname}{url.path}" if url else ""
            parameters = parse_qs(url.query) or None
            return HttpRequest(
                url=full_path,
                http_method=request.get("http_method", ""),
                headers=request.get("headers"),
                parameters=parameters,
                body=request.get("body"),
            )
        except JSONDecodeError as error:
            self.logger.warning(f"Failed to parse log message into request object with error: {error}")
            return None

    def _create_response_from_log_message(self, log_message: AirbyteLogMessage) -> Optional[HttpResponse]:
        # TODO: As a temporary stopgap, the CDK emits response data as a log message string. Ideally this should come in the
        # form of a custom message object defined in the Airbyte protocol, but this unblocks us in the immediate while the
        # protocol change is worked on.
        raw_response = log_message.message.partition("response:")[2]
        try:
            response = json.loads(raw_response)
            body = response.get("body", "{}")
            return HttpResponse(status=response.get("status_code"), body=body, headers=response.get("headers"))
        except JSONDecodeError as error:
            self.logger.warning(f"Failed to parse log message into response object with error: {error}")
            return None

    def _has_reached_limit(self, slices):
        if len(slices) >= self._max_slices:
            return True

        for slice in slices:
            if len(slice.pages) >= self._max_pages_per_slice:
                return True
        return False

    @classmethod
    def _create_configure_catalog(cls, stream_name: str) -> ConfiguredAirbyteCatalog:
        return ConfiguredAirbyteCatalog.parse_obj(
            {
                "streams": [
                    {
                        "stream": {
                            "name": stream_name,
                            "json_schema": {},
                            "supported_sync_modes": ["full_refresh", "incremental"],
                        },
                        "sync_mode": "full_refresh",
                        "destination_sync_mode": "overwrite",
                    }
                ]
            }
        )
