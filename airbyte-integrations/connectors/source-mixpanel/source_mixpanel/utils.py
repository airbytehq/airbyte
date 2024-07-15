#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

import requests
from airbyte_cdk import BackoffStrategy
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler, ErrorResolution, HttpStatusErrorHandler, ResponseAction
from airbyte_protocol.models import FailureType


def read_full_refresh(stream_instance: Stream) -> Iterable[Mapping[str, Any]]:
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for _slice in slices:
        records = stream_instance.read_records(stream_slice=_slice, sync_mode=SyncMode.full_refresh)
        for record in records:
            yield record


# Precompile the regex pattern.
ISO_FORMAT_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})[ t](\d{2}:\d{2}:\d{2})$")


def to_iso_format(s: str) -> str:
    """
    Convert a date string to ISO format if it matches recognized patterns.

    Args:
    - s (str): Input string to be converted.

    Returns:
    - str: Converted string in ISO format or the original string if no recognized pattern is found.
    """
    # Use the precompiled regex pattern to match the date format.
    match = ISO_FORMAT_PATTERN.match(s)
    if match:
        return match.group(1) + "T" + match.group(2)

    return s


def fix_date_time(record: Union[Mapping[str, Any], Dict[str, Any], List[Any]]) -> None:
    """
    Recursively process a data structure to fix date and time formats.

    Args:
    - record (dict or list): The input data structure, which can be a dictionary or a list.

    Returns:
    - None: The function modifies the input data structure in place.
    """
    # Define the list of fields that might contain date and time values.
    date_time_fields = {"last_seen", "created", "last_authenticated"}

    if isinstance(record, dict):
        for field, value in list(record.items()):  # Convert to list to avoid runtime errors during iteration.
            if field in date_time_fields and isinstance(value, str):
                record[field] = to_iso_format(value)
            elif isinstance(value, (dict, list)):
                fix_date_time(value)

    elif isinstance(record, list):
        for entry in record:
            fix_date_time(entry)

    return None


class MixpanelStreamErrorHandler(HttpStatusErrorHandler):
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response):
            if response_or_exception.status_code == 400 and "Unable to authenticate request" in response_or_exception.text:
                message = (
                    f"Your credentials might have expired. Please update your config with valid credentials."
                    f" See more details: {response_or_exception.text}"
                )
                return ErrorResolution(
                    response_action=ResponseAction.FAIL,
                    failure_type=FailureType.config_error,
                    error_message=message,
                )
            elif response_or_exception.status_code == 402:
                message = f"Unable to perform a request. Payment Required: {response_or_exception.json()['error']}"
                return ErrorResolution(
                    response_action=ResponseAction.FAIL,
                    failure_type=FailureType.transient_error,
                    error_message=message,
                )
        return super().interpret_response(response_or_exception)


class DateSlicesMixinErrorHandler(HttpStatusErrorHandler):
    def __init__(self, stream: HttpStream, **kwargs):  # type: ignore # noqa
        self.stream = stream
        super().__init__(**kwargs)

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response):
            if (
                response_or_exception.status_code == requests.codes.bad_request
                and "to_date cannot be later than today" in response_or_exception.text
            ):
                self.stream._timezone_mismatch = True
                message = "Your project timezone must be misconfigured. Please set it to the one defined in your Mixpanel project settings. Stopping current stream sync."
                return ErrorResolution(
                    response_action=ResponseAction.IGNORE,
                    failure_type=FailureType.config_error,
                    error_message=message,
                )
        return super().interpret_response(response_or_exception)


class ExportErrorHandler(MixpanelStreamErrorHandler, DateSlicesMixinErrorHandler):
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response):
            try:
                # trying to parse response to avoid ConnectionResetError and retry if it occurs
                self.stream.iter_dicts(response_or_exception.iter_lines(decode_unicode=True))
            except ConnectionResetError:
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",  # type: ignore[union-attr]
                )
        return super().interpret_response(response_or_exception)


class MixpanelStreamBackoffStrategy(BackoffStrategy):
    def __init__(self, stream: HttpStream, **kwargs):  # type: ignore # noqa
        self.stream = stream
        super().__init__(**kwargs)

    def backoff_time(
        self, response_or_exception: Optional[Union[requests.Response, requests.RequestException]], **kwargs: Any
    ) -> Optional[float]:
        if isinstance(response_or_exception, requests.Response):
            retry_after = response_or_exception.headers.get("Retry-After")
            if retry_after:
                self._logger.debug(f"API responded with `Retry-After` header: {retry_after}")
                return float(retry_after)

        self.stream.retries += 1
        return 2**self.stream.retries * 60  # type: ignore[no-any-return]
