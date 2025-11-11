#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, Iterator, List, Mapping, Optional

from airbyte_cdk.connector_builder.models import (
    AuxiliaryRequest,
    HttpRequest,
    HttpResponse,
    StreamReadPages,
)
from airbyte_cdk.models import (
    AirbyteMessage,
)
from airbyte_cdk.utils.datetime_format_inferrer import DatetimeFormatInferrer
from airbyte_cdk.utils.schema_inferrer import (
    SchemaInferrer,
)

from .helpers import (
    airbyte_message_to_json,
    handle_current_page,
    handle_current_slice,
    handle_log_message,
    handle_record_message,
    is_async_auxiliary_request,
    is_config_update_message,
    is_log_message,
    is_page_http_request_for_different_stream,
    is_record_message,
    is_state_message,
    is_trace_with_error,
    parse_slice_description,
    should_close_page,
    should_close_page_for_slice,
    should_process_slice_descriptor,
)
from .types import MESSAGE_GROUPS


def get_message_groups(
    messages: Iterator[AirbyteMessage],
    schema_inferrer: SchemaInferrer,
    datetime_format_inferrer: DatetimeFormatInferrer,
    limit: int,
    stream_name: str,
) -> MESSAGE_GROUPS:
    """
    Processes an iterator of AirbyteMessage objects to group and yield messages based on their type and sequence.

    This function iterates over the provided messages until the number of record messages processed reaches the specified limit.
    It accumulates messages into pages and slices, handling various types of messages such as log, trace (with errors), record,
    configuration update, and state messages. The function makes use of helper routines to:
        - Convert messages to JSON.
        - Determine when to close a page or a slice.
        - Parse slice descriptors.
        - Handle log messages and auxiliary requests.
        - Process record messages while inferring schema and datetime formats.

    Depending on the incoming message type, it may yield:
        - StreamReadSlices objects when a slice is completed.
        - Auxiliary HTTP requests/responses generated from log messages.
        - Error trace messages if encountered.
        - Configuration update messages.

    Parameters:
        messages (Iterator[AirbyteMessage]): An iterator yielding AirbyteMessage instances.
        schema_inferrer (SchemaInferrer): An instance used to infer and update schema based on record messages.
        datetime_format_inferrer (DatetimeFormatInferrer): An instance used to infer datetime formats from record messages.
        limit (int): The maximum number of record messages to process before stopping.

    Yields:
        Depending on the type of message processed, one or more of the following:
            - StreamReadSlices: A grouping of pages within a slice along with the slice descriptor and state.
            - HttpRequest/HttpResponse: Auxiliary request/response information derived from log messages.
            - TraceMessage: Error details when a trace message with errors is encountered.
            - ControlMessage: Configuration update details.

    Notes:
        The function depends on several helper functions (e.g., airbyte_message_to_json, should_close_page,
        handle_current_page, parse_slice_description, handle_log_message, and others) to encapsulate specific behavior.
        It maintains internal state for grouping pages and slices, ensuring that related messages are correctly aggregated
        and yielded as complete units.
    """

    records_count = 0
    at_least_one_page_in_group = False
    current_page_records: List[Mapping[str, Any]] = []
    current_slice_descriptor: Optional[Dict[str, Any]] = None
    current_slice_pages: List[StreamReadPages] = []
    current_page_request: Optional[HttpRequest] = None
    current_page_response: Optional[HttpResponse] = None
    latest_state_message: Optional[Dict[str, Any]] = None
    slice_auxiliary_requests: List[AuxiliaryRequest] = []

    while message := next(messages, None):
        json_message = airbyte_message_to_json(message)

        if is_page_http_request_for_different_stream(json_message, stream_name):
            continue

        if should_close_page(at_least_one_page_in_group, message, json_message):
            current_page_request, current_page_response = handle_current_page(
                current_page_request,
                current_page_response,
                current_slice_pages,
                current_page_records,
            )

        if should_close_page_for_slice(at_least_one_page_in_group, message):
            yield handle_current_slice(
                current_slice_pages,
                current_slice_descriptor,
                latest_state_message,
                slice_auxiliary_requests,
            )
            current_slice_descriptor = parse_slice_description(message.log.message)  # type: ignore
            current_slice_pages = []
            at_least_one_page_in_group = False
        elif should_process_slice_descriptor(message):
            # parsing the first slice
            current_slice_descriptor = parse_slice_description(message.log.message)  # type: ignore
        elif is_log_message(message):
            (
                at_least_one_page_in_group,
                current_page_request,
                current_page_response,
                auxiliary_request,
                log_message,
            ) = handle_log_message(
                message,
                json_message,
                at_least_one_page_in_group,
                current_page_request,
                current_page_response,
            )

            if auxiliary_request:
                if is_async_auxiliary_request(auxiliary_request):
                    slice_auxiliary_requests.append(auxiliary_request)
                else:
                    yield auxiliary_request

            if log_message:
                yield log_message
        elif is_trace_with_error(message):
            if message.trace is not None:
                yield message.trace
        elif is_record_message(message):
            records_count = handle_record_message(
                message,
                schema_inferrer,
                datetime_format_inferrer,
                records_count,
                current_page_records,
            )
        elif is_config_update_message(message):
            if message.control is not None:
                yield message.control
        elif is_state_message(message):
            latest_state_message = message.state  # type: ignore

    else:
        if current_page_request or current_page_response or current_page_records:
            handle_current_page(
                current_page_request,
                current_page_response,
                current_slice_pages,
                current_page_records,
            )
            yield handle_current_slice(
                current_slice_pages,
                current_slice_descriptor,
                latest_state_message,
                slice_auxiliary_requests,
            )
