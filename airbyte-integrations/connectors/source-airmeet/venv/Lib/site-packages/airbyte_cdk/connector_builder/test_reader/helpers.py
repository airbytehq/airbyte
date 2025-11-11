#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from copy import deepcopy
from json import JSONDecodeError
from typing import Any, Dict, List, Mapping, Optional, Union

from airbyte_cdk.connector_builder.models import (
    AuxiliaryRequest,
    HttpRequest,
    HttpResponse,
    StreamReadPages,
    StreamReadSlices,
)
from airbyte_cdk.models import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteStateBlob,
    AirbyteStateMessage,
    OrchestratorType,
    TraceType,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.utils.slice_logger import SliceLogger
from airbyte_cdk.sources.utils.types import JsonType
from airbyte_cdk.utils.datetime_format_inferrer import DatetimeFormatInferrer
from airbyte_cdk.utils.schema_inferrer import (
    SchemaInferrer,
)

from .types import ASYNC_AUXILIARY_REQUEST_TYPES, LOG_MESSAGES_OUTPUT_TYPE

# -------
# Parsers
# -------


def airbyte_message_to_json(message: AirbyteMessage) -> Optional[Dict[str, JsonType]]:
    """
    Converts an AirbyteMessage to a JSON dictionary if its type is LOG.

    This function attempts to parse the 'log' field of the given AirbyteMessage when its type is MessageType.LOG.
    If the parsed JSON object exists but is not a dictionary, a ValueError is raised. If the message is not of type LOG,
    the function returns None.

    Parameters:
        message (AirbyteMessage): The AirbyteMessage instance containing the log data.

    Returns:
        Optional[Dict[str, JsonType]]: The parsed log message as a dictionary if the message type is LOG, otherwise None.

    Raises:
        ValueError: If the parsed log message is not a dictionary.
    """
    if is_log_message(message):
        json_object = parse_json(message.log)  # type: ignore

        if json_object is not None and not isinstance(json_object, dict):
            raise ValueError(
                f"Expected log message to be a dict, got {json_object} of type {type(json_object)}"
            )

        return json_object
    return None


def clean_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cleans the configuration dictionary by removing all keys that start with a double underscore.

    This function creates a deep copy of the provided configuration dictionary and iterates
    over its keys, deleting any key that begins with '__'. This is useful for filtering out
    internal or meta-data fields that are not meant to be part of the final configuration.

    Args:
        config (Dict[str, Any]): The input configuration dictionary containing various key-value pairs.

    Returns:
        Dict[str, Any]: A deep copy of the original configuration with keys starting with '__' removed.
    """
    cleaned_config = deepcopy(config)
    for key in config.keys():
        if key.startswith("__"):
            del cleaned_config[key]
    return cleaned_config


def create_request_from_log_message(json_http_message: Dict[str, Any]) -> HttpRequest:
    """
    Creates an HttpRequest object from the provided JSON-formatted log message.

    This function parses a dictionary that represents a logged HTTP message, extracting the URL, HTTP method,
    headers, and body from nested dictionary structures. It is assumed that the expected keys and nested keys exist
    or default values are used.

    Parameters:
        json_http_message (Dict[str, Any]):
            A dictionary containing log message details with the following expected structure:
                {
                    "url": {
                        "full": "<full_url>"
                    },
                    "http": {
                        "request": {
                            "method": "<HTTP_method>",
                            "headers": <headers>,
                            "body": {
                                "content": "<body_content>"
                            }
                        }
                    }
                }

    Returns:
        HttpRequest:
            An HttpRequest instance initialized with:
                - url: Extracted from json_http_message["url"]["full"], defaults to an empty string if missing.
                - http_method: Extracted from json_http_message["http"]["request"]["method"], defaults to an empty string if missing.
                - headers: Extracted from json_http_message["http"]["request"]["headers"].
                - body: Extracted from json_http_message["http"]["request"]["body"]["content"], defaults to an empty string if missing.
    """
    url = json_http_message.get("url", {}).get("full", "")
    request = json_http_message.get("http", {}).get("request", {})
    return HttpRequest(
        url=url,
        http_method=request.get("method", ""),
        headers=request.get("headers"),
        body=request.get("body", {}).get("content", ""),
    )


def create_response_from_log_message(json_http_message: Dict[str, Any]) -> HttpResponse:
    """
    Generate an HttpResponse instance from a JSON log message containing HTTP response details.

    Parameters:
        json_http_message (Dict[str, Any]): A dictionary representing a JSON-encoded HTTP message.
            It should include an "http" key with a nested "response" dictionary that contains:
                - "status_code": The HTTP status code.
                - "body": A dictionary with a "content" key for the response body.
                - "headers": The HTTP response headers.

    Returns:
        HttpResponse: An HttpResponse object constructed from the extracted status code, body content, and headers.
    """
    response = json_http_message.get("http", {}).get("response", {})
    body = response.get("body", {}).get("content", "")
    return HttpResponse(
        status=response.get("status_code"), body=body, headers=response.get("headers")
    )


def parse_json(log_message: AirbyteLogMessage) -> JsonType:
    """
    Parse and extract a JSON object from an Airbyte log message.

    This function attempts to decode the JSON string contained in the message field
    of the provided AirbyteLogMessage instance. If the decoding process fails due to
    malformed JSON, the function returns None.

    Args:
        log_message (AirbyteLogMessage): A log message object containing a JSON-formatted string in its 'message' attribute.

    Returns:
        JsonType: The parsed JSON object if decoding is successful; otherwise, None.
    """
    # TODO: As a temporary stopgap, the CDK emits request/response data as a log message string. Ideally this should come in the
    # form of a custom message object defined in the Airbyte protocol, but this unblocks us in the immediate while the
    # protocol change is worked on.
    try:
        json_object: JsonType = json.loads(log_message.message)
        return json_object
    except JSONDecodeError:
        return None


def parse_slice_description(log_message: str) -> Dict[str, Any]:
    """
    Parses a log message containing a JSON payload and returns it as a dictionary.

    The function removes a predefined logging prefix (defined by the constant
    SliceLogger.SLICE_LOG_PREFIX) from the beginning of the log message and then
    parses the remaining string as JSON.

    Parameters:
        log_message (str): The log message string that includes the JSON payload,
                        prefixed by SliceLogger.SLICE_LOG_PREFIX.

    Returns:
        Dict[str, Any]: A dictionary resulting from parsing the modified log message.

    Raises:
        json.JSONDecodeError: If the log message (after prefix removal) is not a valid JSON.
    """
    return json.loads(log_message.replace(SliceLogger.SLICE_LOG_PREFIX, "", 1))  # type: ignore


# -------
# Conditions
# -------


def should_close_page(
    at_least_one_page_in_group: bool,
    message: AirbyteMessage,
    json_message: Optional[Dict[str, Any]],
) -> bool:
    """
    Determines whether a page should be closed based on its content and state.

    Args:
        at_least_one_page_in_group (bool): Indicates if there is at least one page in the group.
        message (AirbyteMessage): The message object containing details such as type and log information.
        json_message (Optional[Dict[str, Any]]): A JSON representation of the message that may provide additional context,
            particularly for HTTP requests.

    Returns:
        bool: True if all of the following conditions are met:
            - There is at least one page in the group.
            - The message type is MessageType.LOG.
            - Either the JSON message corresponds to a page HTTP request (as determined by _is_page_http_request)
            or the log message starts with "slice:".
        Otherwise, returns False.
    """
    return (
        at_least_one_page_in_group
        and is_log_message(message)
        and (
            is_page_http_request(json_message)
            or message.log.message.startswith(SliceLogger.SLICE_LOG_PREFIX)  # type: ignore[union-attr] # AirbyteMessage with MessageType.LOG has log.message
        )
    )


def should_process_slice_descriptor(message: AirbyteMessage) -> bool:
    """
    Determines whether the given AirbyteMessage should be processed as a slice descriptor.

    This function checks if the message is a log message and if its log content starts with the
    specific slice log prefix. It is used to filter out messages that represent slice descriptors
    for further processing.

    Parameters:
        message (AirbyteMessage): The message to evaluate.

    Returns:
        bool: True if the message is a log message whose log message starts with the predefined
            slice log prefix, indicating it is a slice descriptor; otherwise, False.
    """
    return is_log_message(message) and message.log.message.startswith(  # type: ignore
        SliceLogger.SLICE_LOG_PREFIX
    )


def should_close_page_for_slice(at_least_one_page_in_group: bool, message: AirbyteMessage) -> bool:
    """
    Determines whether the current slice page should be closed.

    This function checks if there is at least one page in the current group and if further processing
    of the slice descriptor is required based on the provided Airbyte message.

    Args:
        at_least_one_page_in_group (bool): Indicates if at least one page already exists in the slice group.
        message (AirbyteMessage): The message containing the slice descriptor information to be evaluated.

    Returns:
        bool: True if both conditions are met and the slice page needs to be closed; otherwise, False.
    """
    return at_least_one_page_in_group and should_process_slice_descriptor(message)


def is_page_http_request_for_different_stream(
    json_message: Optional[Dict[str, Any]], stream_name: str
) -> bool:
    """
    Determines whether a given JSON message represents a page HTTP request for a different stream.

    This function checks if the provided JSON message is a page HTTP request, and if the stream name in the log is
    different from the provided stream name.

    This is needed because dynamic streams result in extra page HTTP requests for the dynamic streams that we want to ignore
    when they do not match the stream that is being read.

    Args:
        json_message (Optional[Dict[str, Any]]): The JSON message to evaluate.
        stream_name (str): The name of the stream to compare against.

    Returns:
        bool: True if the JSON message is a page HTTP request for a different stream, False otherwise.
    """
    if not json_message or not is_page_http_request(json_message):
        return False

    message_stream_name: str | None = (
        json_message.get("airbyte_cdk", {}).get("stream", {}).get("name", None)
    )
    if message_stream_name is None:
        return False

    return message_stream_name != stream_name


def is_page_http_request(json_message: Optional[Dict[str, Any]]) -> bool:
    """
    Determines whether a given JSON message represents a page HTTP request.

    This function checks if the provided JSON message qualifies as a page HTTP request by verifying that:
    1. The JSON message exists.
    2. The JSON message is recognized as a valid HTTP log.
    3. The JSON message is not classified as an auxiliary HTTP request.

    Args:
        json_message (Optional[Dict[str, Any]]): A dictionary containing the JSON message to be evaluated.
            If None or empty, the message will not be considered a page HTTP request.

    Returns:
        bool: True if the JSON message is a valid HTTP log and not an auxiliary HTTP request; otherwise, False.
    """
    if not json_message:
        return False
    else:
        return is_http_log(json_message) and not is_auxiliary_http_request(json_message)


def is_http_log(message: Dict[str, JsonType]) -> bool:
    """
    Determine if the provided log message represents an HTTP log.

    This function inspects the given message dictionary for the presence of the "http" key.
    If the key exists and its value is truthy, the function interprets the message as an HTTP log.

    Args:
        message (Dict[str, JsonType]): A dictionary containing log data. It may include an "http" key
            whose truthy value indicates an HTTP log.

    Returns:
        bool: True if the message is an HTTP log (i.e., "http" exists and is truthy); otherwise, False.
    """
    return bool(message.get("http", False))


def is_auxiliary_http_request(message: Optional[Dict[str, Any]]) -> bool:
    """
    Determines if the provided message represents an auxiliary HTTP request.

    A auxiliary request is a request that is performed and will not directly lead to record for the specific stream it is being queried.

    A couple of examples are:
        * OAuth authentication
        * Substream slice generation

    Parameters:
        message (Optional[Dict[str, Any]]): A dictionary representing a log message for an HTTP request.
            The dictionary may contain nested keys indicating whether the request is auxiliary.

    Returns:
        bool: True if the message is an HTTP log and indicates an auxiliary request; otherwise, False.
    """
    if not message:
        return False

    return is_http_log(message) and message.get("http", {}).get("is_auxiliary", False)


def is_async_auxiliary_request(message: AuxiliaryRequest) -> bool:
    return message.type in ASYNC_AUXILIARY_REQUEST_TYPES


def is_log_message(message: AirbyteMessage) -> bool:
    """
    Determines whether the provided message is of type LOG.

    Args:
        message (AirbyteMessage): The message to evaluate.

    Returns:
        bool: True if the message's type is LOG, otherwise False.
    """
    return message.type == MessageType.LOG  # type: ignore


def is_trace_with_error(message: AirbyteMessage) -> bool:
    """
    Determines whether the provided AirbyteMessage is a TRACE message with an error.

    This function checks if the message's type is TRACE and that its trace component is of type ERROR.

    Parameters:
        message (AirbyteMessage): The Airbyte message to be evaluated.

    Returns:
        bool: True if the message is a TRACE message with an error, False otherwise.
    """
    return message.type == MessageType.TRACE and message.trace.type == TraceType.ERROR  # type: ignore


def is_record_message(message: AirbyteMessage) -> bool:
    """
    Determines whether the provided Airbyte message represents a record.

    Parameters:
        message (AirbyteMessage): The message instance to check. It should include a 'type' attribute that is comparable to MessageType.RECORD.

    Returns:
        bool: True if the message type is RECORD, otherwise False.
    """
    return message.type == MessageType.RECORD  # type: ignore


def is_config_update_message(message: AirbyteMessage) -> bool:
    """
    Determine whether the provided AirbyteMessage represents a connector configuration update.

    This function evaluates if the message is a control message and if its control type
    matches that of a connector configuration update (i.e., OrchestratorType.CONNECTOR_CONFIG).
    It is primarily used to filter messages related to configuration updates in the data pipeline.

    Parameters:
        message (AirbyteMessage): The message object to be evaluated.

    Returns:
        bool: True if the message is a connector configuration update message, False otherwise.
    """
    return (  # type: ignore
        message.type == MessageType.CONTROL
        and message.control.type == OrchestratorType.CONNECTOR_CONFIG  # type: ignore
    )


def is_state_message(message: AirbyteMessage) -> bool:
    """
    Determines whether the provided AirbyteMessage is a state message.

    Parameters:
        message (AirbyteMessage): The message to inspect.

    Returns:
        bool: True if the message's type is MessageType.STATE, False otherwise.
    """
    return message.type == MessageType.STATE  # type: ignore


# -------
# Handlers
# -------


def handle_current_slice(
    current_slice_pages: List[StreamReadPages],
    current_slice_descriptor: Optional[Dict[str, Any]] = None,
    latest_state_message: Optional[Dict[str, Any]] = None,
    auxiliary_requests: Optional[List[AuxiliaryRequest]] = None,
) -> StreamReadSlices:
    """
    Handles the current slice by packaging its pages, descriptor, and state into a StreamReadSlices instance.

    Args:
        current_slice_pages (List[StreamReadPages]): The pages to be included in the slice.
        current_slice_descriptor (Optional[Dict[str, Any]]): Descriptor for the current slice, optional.
        latest_state_message (Optional[Dict[str, Any]]): The latest state message, optional.
        auxiliary_requests (Optional[List[AuxiliaryRequest]]): The auxiliary requests to include, optional.

    Returns:
        StreamReadSlices: An object containing the current slice's pages, descriptor, and state.
    """
    return StreamReadSlices(
        pages=current_slice_pages,
        slice_descriptor=current_slice_descriptor,
        state=[convert_state_blob_to_mapping(latest_state_message)] if latest_state_message else [],
        auxiliary_requests=auxiliary_requests if auxiliary_requests else [],
    )


def handle_current_page(
    current_page_request: Optional[HttpRequest],
    current_page_response: Optional[HttpResponse],
    current_slice_pages: List[StreamReadPages],
    current_page_records: List[Mapping[str, Any]],
) -> tuple[None, None]:
    """
    Closes the current page by appending its request, response, and records
    to the list of pages and clearing the current page records.

    Args:
        current_page_request (Optional[HttpRequest]): The HTTP request associated with the current page.
        current_page_response (Optional[HttpResponse]): The HTTP response associated with the current page.
        current_slice_pages (List[StreamReadPages]): A list to append the current page information.
        current_page_records (List[Mapping[str, Any]]): The records of the current page to be cleared after processing.

    Returns:
        tuple[None, None]: A tuple indicating that no values are returned.
    """

    current_slice_pages.append(
        StreamReadPages(
            request=current_page_request,
            response=current_page_response,
            records=deepcopy(current_page_records),  # type: ignore [arg-type]
        )
    )
    current_page_records.clear()

    return None, None


def handle_auxiliary_request(json_message: Dict[str, JsonType]) -> AuxiliaryRequest:
    """
    Parses the provided JSON message and constructs an AuxiliaryRequest object by extracting
    relevant fields from nested dictionaries.

    This function retrieves and validates the "airbyte_cdk", "stream", and "http" dictionaries
    from the JSON message. It raises a ValueError if any of these are not of type dict. A title
    is dynamically created by checking if the stream is a substream and then combining a prefix
    with the "title" field from the "http" dictionary. The function also uses helper functions
    to generate the request and response portions of the AuxiliaryRequest.

    Parameters:
        json_message (Dict[str, JsonType]): A dictionary representing the JSON log message containing
        auxiliary request details.

    Returns:
        AuxiliaryRequest: An object containing the formatted title, description, request, and response
        extracted from the JSON message.

    Raises:
        ValueError: If any of the "airbyte_cdk", "stream", or "http" fields is not a dictionary.
    """

    airbyte_cdk = get_airbyte_cdk_from_message(json_message)
    stream = get_stream_from_airbyte_cdk(airbyte_cdk)
    title_prefix = get_auxiliary_request_title_prefix(stream)
    http = get_http_property_from_message(json_message)
    request_type = get_auxiliary_request_type(stream, http)

    title = title_prefix + str(http.get("title", None))
    description = str(http.get("description", None))
    request = create_request_from_log_message(json_message)
    response = create_response_from_log_message(json_message)

    return AuxiliaryRequest(
        title=title,
        type=request_type,
        description=description,
        request=request,
        response=response,
    )


def handle_log_message(
    message: AirbyteMessage,
    json_message: Dict[str, JsonType] | None,
    at_least_one_page_in_group: bool,
    current_page_request: Optional[HttpRequest],
    current_page_response: Optional[HttpResponse],
) -> LOG_MESSAGES_OUTPUT_TYPE:
    """
    Process a log message by handling both HTTP-specific and auxiliary log entries.

    Parameters:
        message (AirbyteMessage): The original log message received.
        json_message (Dict[str, JsonType] | None): A parsed JSON representation of the log message, if available.
        at_least_one_page_in_group (bool): Indicates whether at least one page within the group has been processed.
        current_page_request (Optional[HttpRequest]): The HTTP request object corresponding to the current page, if any.
        current_page_response (Optional[HttpResponse]): The HTTP response object corresponding to the current page, if any.

    Returns:
        LOG_MESSAGES_OUTPUT_TYPE: A tuple containing:
            - A boolean flag that determines whether the group contains at least one page.
            - An updated HttpRequest for the current page (if applicable).
            - An updated HttpResponse for the current page (if applicable).
            - The auxiliary log message, which might be the original HTTP log or another log field.

    Note:
        If the parsed JSON message indicates an HTTP log and represents an auxiliary HTTP request,
        the auxiliary log is handled via _handle_auxiliary_request. Otherwise, if the JSON log is a standard HTTP log,
        the function updates the current page's request and response objects by generating them from the log message.
    """
    auxiliary_request = None
    log_message = None

    if json_message is not None and is_http_log(json_message):
        if is_auxiliary_http_request(json_message):
            auxiliary_request = handle_auxiliary_request(json_message)
        else:
            at_least_one_page_in_group = True
            current_page_request = create_request_from_log_message(json_message)
            current_page_response = create_response_from_log_message(json_message)
    else:
        log_message = message.log

    return (
        at_least_one_page_in_group,
        current_page_request,
        current_page_response,
        auxiliary_request,
        log_message,
    )


def handle_record_message(
    message: AirbyteMessage,
    schema_inferrer: SchemaInferrer,
    datetime_format_inferrer: DatetimeFormatInferrer,
    records_count: int,
    current_page_records: List[Mapping[str, Any]],
) -> int:
    """
    Processes an Airbyte record message by updating the current batch and accumulating schema and datetime format information.

    Parameters:
        message (AirbyteMessage): The Airbyte message to process. Expected to have a 'type' attribute and, if of type RECORD, a 'record' attribute containing the record data.
        schema_inferrer (SchemaInferrer): An instance responsible for inferring and accumulating schema details based on the record data.
        datetime_format_inferrer (DatetimeFormatInferrer): An instance responsible for inferring and accumulating datetime format information from the record data.
        records_count (int): The current count of processed records. This value is incremented if the message is a record.
        current_page_records (List[Mapping[str, Any]]): A list where the data of processed record messages is accumulated.

    Returns:
        int: The updated record count after processing the message.
    """
    if message.type == MessageType.RECORD:
        current_page_records.append(message.record.data)  # type: ignore
        records_count += 1
        schema_inferrer.accumulate(message.record)  # type: ignore
        datetime_format_inferrer.accumulate(message.record)  # type: ignore

    return records_count


# -------
# Reusable Getters
# -------


def get_airbyte_cdk_from_message(json_message: Dict[str, JsonType]) -> dict:  # type: ignore
    """
    Retrieves the "airbyte_cdk" dictionary from the provided JSON message.

    This function validates that the extracted "airbyte_cdk" is of type dict,
    raising a ValueError if the validation fails.

    Parameters:
        json_message (Dict[str, JsonType]): A dictionary representing the JSON message.

    Returns:
        dict: The "airbyte_cdk" dictionary extracted from the JSON message.

    Raises:
        ValueError: If the "airbyte_cdk" field is not a dictionary.
    """
    airbyte_cdk = json_message.get("airbyte_cdk", {})

    if not isinstance(airbyte_cdk, dict):
        raise ValueError(
            f"Expected airbyte_cdk to be a dict, got {airbyte_cdk} of type {type(airbyte_cdk)}"
        )

    return airbyte_cdk


def get_stream_from_airbyte_cdk(airbyte_cdk: dict) -> dict:  # type: ignore
    """
    Retrieves the "stream" dictionary from the provided "airbyte_cdk" dictionary.

    This function ensures that the extracted "stream" is of type dict,
    raising a ValueError if the validation fails.

    Parameters:
        airbyte_cdk (dict): The dictionary representing the Airbyte CDK data.

    Returns:
        dict: The "stream" dictionary extracted from the Airbyte CDK data.

    Raises:
        ValueError: If the "stream" field is not a dictionary.
    """

    stream = airbyte_cdk.get("stream", {})

    if not isinstance(stream, dict):
        raise ValueError(f"Expected stream to be a dict, got {stream} of type {type(stream)}")

    return stream


def get_auxiliary_request_title_prefix(stream: dict) -> str:  # type: ignore
    """
    Generates a title prefix based on the stream type.
    """
    return "Parent stream: " if stream.get("is_substream", False) else ""


def get_http_property_from_message(json_message: Dict[str, JsonType]) -> dict:  # type: ignore
    """
    Retrieves the "http" dictionary from the provided JSON message.

    This function validates that the extracted "http" is of type dict,
    raising a ValueError if the validation fails.

    Parameters:
        json_message (Dict[str, JsonType]): A dictionary representing the JSON message.

    Returns:
        dict: The "http" dictionary extracted from the JSON message.

    Raises:
        ValueError: If the "http" field is not a dictionary.
    """
    http = json_message.get("http", {})

    if not isinstance(http, dict):
        raise ValueError(f"Expected http to be a dict, got {http} of type {type(http)}")

    return http


def get_auxiliary_request_type(stream: dict, http: dict) -> str:  # type: ignore
    """
    Determines the type of the auxiliary request based on the stream and HTTP properties.
    """
    return "PARENT_STREAM" if stream.get("is_substream", False) else str(http.get("type", None))


def convert_state_blob_to_mapping(
    state_message: Union[AirbyteStateMessage, Dict[str, Any]],
) -> Dict[str, Any]:
    """
    The AirbyteStreamState stores state as an AirbyteStateBlob which deceivingly is not
    a dictionary, but rather a list of kwargs fields. This in turn causes it to not be
    properly turned into a dictionary when translating this back into response output
    by the connector_builder_handler using asdict()
    """

    if isinstance(state_message, AirbyteStateMessage) and state_message.stream:
        state_value = state_message.stream.stream_state
        if isinstance(state_value, AirbyteStateBlob):
            state_value_mapping = {k: v for k, v in state_value.__dict__.items()}
            state_message.stream.stream_state = state_value_mapping  # type: ignore  # we intentionally set this as a Dict so that StreamReadSlices is translated properly in the resulting HTTP response
        return state_message  # type: ignore  # See above, but when this is an AirbyteStateMessage we must convert AirbyteStateBlob to a Dict
    else:
        return state_message  # type: ignore  # This is guaranteed to be a Dict since we check isinstance AirbyteStateMessage above
