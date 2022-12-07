#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import logging
from json import JSONDecodeError
from typing import Any, Dict, Iterable, Optional, Union
from urllib.parse import parse_qs, urljoin, urlparse

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Type
from fastapi import Body, HTTPException
from jsonschema import ValidationError

from connector_builder.generated.apis.default_api_interface import DefaultApi
from connector_builder.generated.models.http_request import HttpRequest
from connector_builder.generated.models.http_response import HttpResponse
from connector_builder.generated.models.stream_read import StreamRead
from connector_builder.generated.models.stream_read_pages import StreamReadPages
from connector_builder.generated.models.stream_read_request_body import StreamReadRequestBody
from connector_builder.generated.models.stream_read_slices import StreamReadSlices
from connector_builder.generated.models.streams_list_read import StreamsListRead
from connector_builder.generated.models.streams_list_read_streams import StreamsListReadStreams
from connector_builder.generated.models.streams_list_request_body import StreamsListRequestBody
from connector_builder.impl.low_code_cdk_adapter import LowCodeSourceAdapter


class DefaultApiImpl(DefaultApi):
    logger = logging.getLogger("airbyte.connector-builder")

    async def get_manifest_template(self) -> str:
        return """version: "0.1.0"
definitions:
  selector:
    extractor:
      field_pointer: []
  requester:
    url_base: "https://example.com"
    http_method: "GET"
    authenticator:
      type: BearerAuthenticator
      api_token: "{{ config['api_key'] }}"
  retriever:
    record_selector:
      $ref: "*ref(definitions.selector)"
    paginator:
      type: NoPagination
    requester:
      $ref: "*ref(definitions.requester)"
  base_stream:
    retriever:
      $ref: "*ref(definitions.retriever)"
  customers_stream:
    $ref: "*ref(definitions.base_stream)"
    $options:
      name: "customers"
      primary_key: "id"
      path: "/example"

streams:
  - "*ref(definitions.customers_stream)"

check:
  stream_names:
    - "customers"

spec:
  documentation_url: https://docsurl.com
  connection_specification:
    title: Source Name Spec # 'TODO: Replace this with the name of your source.'
    type: object
    required:
      - api_key
    additionalProperties: true
    properties:
      # 'TODO: This schema defines the configuration required for the source. This usually involves metadata such as database and/or authentication information.':
      api_key:
        type: string
        description: API Key
"""

    async def list_streams(self, streams_list_request_body: StreamsListRequestBody = Body(None, description="")) -> StreamsListRead:
        """
        Takes in a low code manifest and a config to resolve the list of streams that are available for testing
        :param streams_list_request_body: Input parameters to retrieve the list of available streams
        :return: Stream objects made up of a stream name and the HTTP URL it will send requests to
        """
        adapter = self._create_low_code_adapter(manifest=streams_list_request_body.manifest)

        stream_list_read = []
        try:
            for http_stream in adapter.get_http_streams(streams_list_request_body.config):
                stream_list_read.append(
                    StreamsListReadStreams(
                        name=http_stream.name,
                        url=urljoin(http_stream.url_base, http_stream.path()),
                    )
                )
        except Exception as error:
            raise HTTPException(status_code=400, detail=f"Could not list streams with with error: {error.args[0]}")
        return StreamsListRead(streams=stream_list_read)

    async def read_stream(self, stream_read_request_body: StreamReadRequestBody = Body(None, description="")) -> StreamRead:
        """
        Using the provided manifest and config, invokes a sync for the specified stream and returns groups of Airbyte messages
        that are produced during the read operation
        :param stream_read_request_body: Input parameters to trigger the read operation for a stream
        :return: Airbyte record messages produced by the sync grouped by slice and page
        """
        adapter = self._create_low_code_adapter(manifest=stream_read_request_body.manifest)

        single_slice = StreamReadSlices(pages=[])
        log_messages = []
        try:
            for message_group in self._get_message_groups(
                    adapter.read_stream(stream_read_request_body.stream, stream_read_request_body.config)
            ):
                if isinstance(message_group, AirbyteLogMessage):
                    log_messages.append({"message": message_group.message})
                else:
                    single_slice.pages.append(message_group)
        except Exception as error:
            # TODO: We're temporarily using FastAPI's default exception model. Ideally we should use exceptions defined in the OpenAPI spec
            raise HTTPException(status_code=400, detail=f"Could not perform read with with error: {error.args[0]}")

        return StreamRead(logs=log_messages, slices=[single_slice])

    def _get_message_groups(self, messages: Iterable[AirbyteMessage]) -> Iterable[Union[StreamReadPages, AirbyteLogMessage]]:
        """
        Message groups are partitioned according to when request log messages are received. Subsequent response log messages
        and record messages belong to the prior request log message and when we encounter another request, append the latest
        message group.

        Messages received from the CDK read operation will always arrive in the following order:
        {type: LOG, log: {message: "request: ..."}}
        {type: LOG, log: {message: "response: ..."}}
        ... 0 or more record messages
        {type: RECORD, record: {data: ...}}
        {type: RECORD, record: {data: ...}}
        Repeats for each request/response made

        Note: The exception is that normal log messages can be received at any time which are not incorporated into grouping
        """
        first_page = True
        current_records = []
        current_page_request: Optional[HttpRequest] = None
        current_page_response: Optional[HttpResponse] = None
        for message in messages:
            if first_page and message.type == Type.LOG and message.log.message.startswith("request:"):
                first_page = False
                request = self._create_request_from_log_message(message.log)
                current_page_request = request
            elif message.type == Type.LOG and message.log.message.startswith("request:"):
                if not current_page_request or not current_page_response:
                    raise ValueError("Every message grouping should have at least one request and response")
                yield StreamReadPages(request=current_page_request, response=current_page_response, records=current_records)
                current_page_request = self._create_request_from_log_message(message.log)
                current_records = []
            elif message.type == Type.LOG and message.log.message.startswith("response:"):
                current_page_response = self._create_response_from_log_message(message.log)
            elif message.type == Type.LOG:
                yield message.log
            elif message.type == Type.RECORD:
                current_records.append(message.record.data)
        else:
            if not current_page_request or not current_page_response:
                raise ValueError("Every message grouping should have at least one request and response")
            yield StreamReadPages(request=current_page_request, response=current_page_response, records=current_records)

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
            body = json.loads(response.get("body", "{}"))
            return HttpResponse(status=response.get("status_code"), body=body, headers=response.get("headers"))
        except JSONDecodeError as error:
            self.logger.warning(f"Failed to parse log message into response object with error: {error}")
            return None

    @staticmethod
    def _create_low_code_adapter(manifest: Dict[str, Any]) -> LowCodeSourceAdapter:
        try:
            return LowCodeSourceAdapter(manifest=manifest)
        except ValidationError as error:
            # TODO: We're temporarily using FastAPI's default exception model. Ideally we should use exceptions defined in the OpenAPI spec
            raise HTTPException(status_code=400, detail=f"Invalid connector manifest with error: {error.message}")
