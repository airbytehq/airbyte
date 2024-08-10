#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import List, Optional, Union

import requests
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_http_response_filter import DefaultHttpResponseFilter
from airbyte_cdk.sources.declarative.types import Record
from airbyte_cdk.sources.streams.http.error_handlers.response_models import (
    DEFAULT_ERROR_RESOLUTION,
    SUCCESS_RESOLUTION,
    ErrorResolution,
    ResponseAction,
)


class USCensusRecordExtractor(RecordExtractor):
    """
    Parses the response from the us census website.

    The US Census provides data in an atypical format,
    which motivated the creation of this source rather
    than using a generic http source.

    * Data are represented in a two-dimensional array
    * Square brackets [ ] hold arrays
    * Values are separated by a , (comma).

    e.g.
        [["STNAME","POP","DATE_","state"],

        ["Alabama","4849377","7","01"],

        ["Alaska","736732","7","02"],

        ["Arizona","6731484","7","04"],

        ["Arkansas","2966369","7","05"],

        ["California","38802500","7","06"]]
    """

    def extract_records(self, response: requests.Response) -> List[Record]:  # type: ignore
        # Where we accumulate a "row" of data until we encounter ']'
        buffer = ""
        # The response is in a tabular format where the first list of strings
        # is the "header" of the table which we use as keys in the final dictionary
        # we produce
        header = []
        # Characters with special meanings which should not be added to the buffer
        # of values
        ignore_chars = [
            "[",
            "\n",
        ]
        # Context: save if previous value is an escape character
        is_prev_escape = False
        # Context: save if we are currently in double quotes
        is_in_quotes = False
        # Placeholder used to save position of commas that are
        # within values, so the .split(',') call does not produce
        # erroneous values
        comma_placeholder = "||comma_placeholder||"

        for response_chunk in response.iter_content(decode_unicode=True):
            if response_chunk == "\\":
                is_prev_escape = True
                continue
            elif response_chunk == '"' and not is_prev_escape:
                # If we are in quotes and encounter
                # closing quotes, we are not within quotes anymore
                # otherwise we are within quotes.
                is_in_quotes = not is_in_quotes
            elif response_chunk == "," and is_in_quotes:
                buffer += comma_placeholder
            elif response_chunk in ignore_chars and not is_prev_escape:
                pass
            elif response_chunk == "]":
                if not header:
                    header = buffer.split(",")
                elif buffer:
                    # Remove the first character from the values since
                    # it's a comma.
                    split_values = buffer.split(",")[1:]
                    # Add back commas originally embedded in values
                    split_values = map(
                        lambda x: x.replace(comma_placeholder, ","),
                        split_values,
                    )
                    # Zip the values we found with the "header"
                    yield dict(
                        zip(
                            header,
                            split_values,
                        )
                    )
                buffer = ""
            else:
                buffer += response_chunk
            is_prev_escape = False


class USCensusErrorHandler(DefaultErrorHandler):
    """
    This Custom Error Handler raises an error when an invalid API key is used.

    In such cases, the status code is 200, so airbyte doesn't raise an error.
    """

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:

        if self.response_filters:
            for response_filter in self.response_filters:
                matched_error_resolution = response_filter.matches(response_or_exception=response_or_exception)
                if matched_error_resolution:
                    return matched_error_resolution
        if isinstance(response_or_exception, requests.Response):
            if response_or_exception.ok:
                if "Invalid Key" in response_or_exception.text:
                    return ErrorResolution(
                        response_action=ResponseAction.FAIL,
                        failure_type=FailureType.config_error,
                        error_message="Failed to perform request. Error: Valid API Key needed.",
                    )
                return SUCCESS_RESOLUTION

        default_reponse_filter = DefaultHttpResponseFilter(parameters={}, config=self.config)
        default_response_filter_resolution = default_reponse_filter.matches(response_or_exception)

        return default_response_filter_resolution if default_response_filter_resolution else DEFAULT_ERROR_RESOLUTION
