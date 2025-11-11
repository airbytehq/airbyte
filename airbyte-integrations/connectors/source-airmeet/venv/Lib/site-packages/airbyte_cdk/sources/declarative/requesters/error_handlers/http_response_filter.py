#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, Mapping, Optional, Set, Union

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.streams.http.error_handlers import JsonErrorMessageParser
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import (
    DEFAULT_ERROR_MAPPING,
)
from airbyte_cdk.sources.streams.http.error_handlers.response_models import (
    ErrorResolution,
    ResponseAction,
)
from airbyte_cdk.sources.types import Config


@dataclass
class HttpResponseFilter:
    """
    Filter to select a response based on its HTTP status code, error message or a predicate.
    If a response matches the filter, the response action, failure_type, and error message are returned as an ErrorResolution object.
    For http_codes declared in the filter, the failure_type will default to `system_error`.
    To override default failure_type use configured failure_type with ResponseAction.FAIL.

    Attributes:
        action (Union[ResponseAction, str]): action to execute if a request matches
        failure_type (Union[ResponseAction, str]): failure type of traced exception if a response matches the filter
        http_codes (Set[int]): http code of matching requests
        error_message_contains (str): error substring of matching requests
        predicate (str): predicate to apply to determine if a request is matching
        error_message (Union[InterpolatedString, str): error message to display if the response matches the filter
    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]
    action: Optional[Union[ResponseAction, str]] = None
    failure_type: Optional[Union[FailureType, str]] = None
    http_codes: Optional[Set[int]] = None
    error_message_contains: Optional[str] = None
    predicate: Union[InterpolatedBoolean, str] = ""
    error_message: Union[InterpolatedString, str] = ""

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        if self.action is not None:
            if (
                self.http_codes is None
                and self.predicate is None
                and self.error_message_contains is None
            ):
                raise ValueError(
                    "HttpResponseFilter requires a filter condition if an action is specified"
                )
            elif isinstance(self.action, str):
                self.action = ResponseAction[self.action]
        self.http_codes = self.http_codes or set()
        if isinstance(self.predicate, str):
            self.predicate = InterpolatedBoolean(condition=self.predicate, parameters=parameters)
        self.error_message = InterpolatedString.create(
            string_or_interpolated=self.error_message, parameters=parameters
        )
        self._error_message_parser = JsonErrorMessageParser()
        if self.failure_type and isinstance(self.failure_type, str):
            self.failure_type = FailureType[self.failure_type]

    def matches(
        self, response_or_exception: Optional[Union[requests.Response, Exception]]
    ) -> Optional[ErrorResolution]:
        filter_action = self._matches_filter(response_or_exception)
        mapped_key = (
            response_or_exception.status_code
            if isinstance(response_or_exception, requests.Response)
            else response_or_exception.__class__
        )

        if isinstance(mapped_key, (int, Exception)):
            default_mapped_error_resolution = self._match_default_error_mapping(mapped_key)
        else:
            default_mapped_error_resolution = None

        if filter_action is not None:
            default_error_message = (
                default_mapped_error_resolution.error_message
                if default_mapped_error_resolution
                else ""
            )
            error_message = None
            if isinstance(response_or_exception, requests.Response):
                error_message = self._create_error_message(response_or_exception)
            error_message = error_message or default_error_message

            if self.failure_type and filter_action == ResponseAction.FAIL:
                failure_type = self.failure_type
            elif default_mapped_error_resolution:
                failure_type = default_mapped_error_resolution.failure_type
            else:
                failure_type = FailureType.system_error

            return ErrorResolution(
                response_action=filter_action,
                failure_type=failure_type,
                error_message=error_message,
            )

        if (
            (isinstance(self.http_codes, list) and len(self.http_codes)) is None
            and self.predicate is None
            and self.error_message_contains is None
        ) and default_mapped_error_resolution:
            return default_mapped_error_resolution

        return None

    def _match_default_error_mapping(
        self, mapped_key: Union[int, type[Exception]]
    ) -> Optional[ErrorResolution]:
        return DEFAULT_ERROR_MAPPING.get(mapped_key)

    def _matches_filter(
        self, response_or_exception: Optional[Union[requests.Response, Exception]]
    ) -> Optional[ResponseAction]:
        """
        Apply the HTTP filter on the response and return the action to execute if it matches
        :param response: The HTTP response to evaluate
        :return: The action to execute. None if the response does not match the filter
        """
        if isinstance(response_or_exception, requests.Response) and (
            response_or_exception.status_code in self.http_codes  # type: ignore # http_codes set is always initialized to a value in __post_init__
            or self._response_matches_predicate(response_or_exception)
            or self._response_contains_error_message(response_or_exception)
        ):
            return self.action  # type: ignore # action is always cast to a ResponseAction not a str
        return None

    @staticmethod
    def _safe_response_json(response: requests.Response) -> dict[str, Any]:
        try:
            return response.json()  # type: ignore # Response.json() returns a dictionary even if the signature does not
        except requests.exceptions.JSONDecodeError:
            return {}

    def _create_error_message(self, response: requests.Response) -> Optional[str]:
        """
        Construct an error message based on the specified message template of the filter.
        :param response: The HTTP response which can be used during interpolation
        :return: The evaluated error message string to be emitted
        """
        return self.error_message.eval(  # type: ignore[no-any-return, union-attr]
            self.config, response=self._safe_response_json(response), headers=response.headers
        )

    def _response_matches_predicate(self, response: requests.Response) -> bool:
        return (
            bool(
                self.predicate.condition  # type:ignore[union-attr]
                and self.predicate.eval(  # type:ignore[union-attr]
                    None,  # type: ignore[arg-type]
                    response=self._safe_response_json(response),
                    headers=response.headers,
                )
            )
            if self.predicate
            else False
        )

    def _response_contains_error_message(self, response: requests.Response) -> bool:
        if not self.error_message_contains:
            return False
        else:
            error_message = self._error_message_parser.parse_response_error_message(
                response=response
            )
            return bool(error_message and self.error_message_contains in error_message)
