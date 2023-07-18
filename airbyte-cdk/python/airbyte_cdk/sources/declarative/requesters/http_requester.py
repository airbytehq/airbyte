#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
from dataclasses import InitVar, dataclass
from functools import lru_cache
from typing import Any, Callable, Mapping, MutableMapping, Optional, Set, Tuple, Union
from urllib.parse import urljoin

import requests
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator, NoAuth
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.exceptions import ReadException
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.error_handlers.error_handler import ErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_action import ResponseAction
from airbyte_cdk.sources.declarative.requesters.error_handlers.response_status import ResponseStatus
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod, Requester
from airbyte_cdk.sources.declarative.types import Config, StreamSlice, StreamState
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, RequestBodyException, UserDefinedBackoffException
from airbyte_cdk.sources.streams.http.http import BODY_REQUEST_METHODS
from airbyte_cdk.sources.streams.http.rate_limiting import default_backoff_handler, user_defined_backoff_handler
from requests.auth import AuthBase


@dataclass
class HttpRequester(Requester):
    """
    Default implementation of a Requester

    Attributes:
        name (str): Name of the stream. Only used for request/response caching
        url_base (Union[InterpolatedString, str]): Base url to send requests to
        path (Union[InterpolatedString, str]): Path to send requests to
        http_method (Union[str, HttpMethod]): HTTP method to use when sending requests
        request_options_provider (Optional[InterpolatedRequestOptionsProvider]): request option provider defining the options to set on outgoing requests
        authenticator (DeclarativeAuthenticator): Authenticator defining how to authenticate to the source
        error_handler (Optional[ErrorHandler]): Error handler defining how to detect and handle errors
        config (Config): The user-provided configuration as specified by the source's spec
    """

    name: str
    url_base: Union[InterpolatedString, str]
    path: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    authenticator: Optional[DeclarativeAuthenticator] = None
    http_method: Union[str, HttpMethod] = HttpMethod.GET
    request_options_provider: Optional[InterpolatedRequestOptionsProvider] = None
    error_handler: Optional[ErrorHandler] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._url_base = InterpolatedString.create(self.url_base, parameters=parameters)
        self._path = InterpolatedString.create(self.path, parameters=parameters)
        if self.request_options_provider is None:
            self._request_options_provider = InterpolatedRequestOptionsProvider(config=self.config, parameters=parameters)
        elif isinstance(self.request_options_provider, dict):
            self._request_options_provider = InterpolatedRequestOptionsProvider(config=self.config, **self.request_options_provider)
        else:
            self._request_options_provider = self.request_options_provider
        self._authenticator = self.authenticator or NoAuth(parameters=parameters)
        self._http_method = HttpMethod[self.http_method] if isinstance(self.http_method, str) else self.http_method
        self.error_handler = self.error_handler
        self._parameters = parameters
        self.decoder = JsonDecoder(parameters={})
        self._session = requests.Session()

        if isinstance(self._authenticator, AuthBase):
            self._session.auth = self._authenticator

    # We are using an LRU cache in should_retry() method which requires all incoming arguments (including self) to be hashable.
    # Dataclasses by default are not hashable, so we need to define __hash__(). Alternatively, we can set @dataclass(frozen=True),
    # but this has a cascading effect where all dataclass fields must also be set to frozen.
    def __hash__(self) -> int:
        return hash(tuple(self.__dict__))

    def get_authenticator(self) -> DeclarativeAuthenticator:
        return self._authenticator

    def get_url_base(self) -> str:
        return os.path.join(self._url_base.eval(self.config), "")

    def get_path(
        self, *, stream_state: Optional[StreamState], stream_slice: Optional[StreamSlice], next_page_token: Optional[Mapping[str, Any]]
    ) -> str:
        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        path = str(self._path.eval(self.config, **kwargs))
        return path.lstrip("/")

    def get_method(self) -> HttpMethod:
        return self._http_method

    # use a tiny cache to limit the memory footprint. It doesn't have to be large because we mostly
    # only care about the status of the last response received
    @lru_cache(maxsize=10)
    def interpret_response_status(self, response: requests.Response) -> ResponseStatus:
        # Cache the result because the HttpStream first checks if we should retry before looking at the backoff time
        if self.error_handler is None:
            raise ValueError("Cannot interpret response status without an error handler")
        return self.error_handler.interpret_response(response)

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return self._request_options_provider.get_request_params(
            stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        )

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._request_options_provider.get_request_headers(
            stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        )

    # fixing request options provider types has a lot of dependencies
    def get_request_body_data(  # type: ignore
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Union[Mapping[str, Any], str]:
        return (
            self._request_options_provider.get_request_body_data(
                stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
            )
            or {}
        )

    # fixing request options provider types has a lot of dependencies
    def get_request_body_json(  # type: ignore
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:
        return self._request_options_provider.get_request_body_json(
            stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
        )

    def request_kwargs(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # todo: there are a few integrations that override the request_kwargs() method, but the use case for why kwargs over existing
        #  constructs is a little unclear. We may revisit this, but for now lets leave it out of the DSL
        return {}

    disable_retries: bool = False
    _DEFAULT_MAX_RETRY = 5
    _DEFAULT_RETRY_FACTOR = 5

    @property
    def max_retries(self) -> Union[int, None]:
        if self.disable_retries:
            return 0
        if self.error_handler is None:
            return self._DEFAULT_MAX_RETRY
        return self.error_handler.max_retries

    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(f"airbyte.HttpRequester.{self.name}")

    def _should_retry(self, response: requests.Response) -> bool:
        """
        Specifies conditions for backoff based on the response from the server.

        By default, back off on the following HTTP response statuses:
         - 429 (Too Many Requests) indicating rate limiting
         - 500s to handle transient server errors

        Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.
        """
        if self.error_handler is None:
            return response.status_code == 429 or 500 <= response.status_code < 600
        return bool(self.interpret_response_status(response).action == ResponseAction.RETRY)

    def _backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        Specifies backoff time.

         This method is called only if should_backoff() returns True for the input request.

         :param response:
         :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
         to the default backoff behavior (e.g using an exponential algorithm).
        """
        if self.error_handler is None:
            return None
        should_retry = self.interpret_response_status(response)
        if should_retry.action != ResponseAction.RETRY:
            raise ValueError(f"backoff_time can only be applied on retriable response action. Got {should_retry.action}")
        assert should_retry.action == ResponseAction.RETRY
        return should_retry.retry_in

    def _error_message(self, response: requests.Response) -> str:
        """
        Constructs an error message which can incorporate the HTTP response received from the partner API.

        :param response: The incoming HTTP response from the partner API
        :return The error message string to be emitted
        """
        return self.interpret_response_status(response).error_message

    def _get_mapping(
        self, method: Callable[..., Optional[Union[Mapping[str, Any], str]]], **kwargs: Any
    ) -> Tuple[Union[Mapping[str, Any], str], Set[str]]:
        """
        Get mapping from the provided method, and get the keys of the mapping.
        If the method returns a string, it will return the string and an empty set.
        If the method returns a dict, it will return the dict and its keys.
        """
        mapping = method(**kwargs) or {}
        keys = set(mapping.keys()) if not isinstance(mapping, str) else set()
        return mapping, keys

    def _get_request_options(
        self,
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        requester_method: Callable[..., Optional[Union[Mapping[str, Any], str]]],
        auth_options_method: Callable[..., Optional[Union[Mapping[str, Any], str]]],
        extra_options: Optional[Union[Mapping[str, Any], str]] = None,
    ) -> Union[Mapping[str, Any], str]:
        """
        Get the request_option from the requester, the authenticator and extra_options passed in.
        Raise a ValueError if there's a key collision
        Returned merged mapping otherwise
        """
        requester_mapping, requester_keys = self._get_mapping(requester_method, stream_slice=stream_slice, next_page_token=next_page_token)
        auth_options_mapping, auth_options_keys = self._get_mapping(auth_options_method)
        extra_options = extra_options or {}
        extra_mapping, extra_keys = self._get_mapping(lambda: extra_options)

        all_mappings = [requester_mapping, auth_options_mapping, extra_mapping]
        all_keys = [requester_keys, auth_options_keys, extra_keys]

        # If more than one mapping is a string, raise a ValueError
        if sum(isinstance(mapping, str) for mapping in all_mappings) > 1:
            raise ValueError("Cannot combine multiple options if one is a string")

        # If any mapping is a string, return it
        for mapping in all_mappings:
            if isinstance(mapping, str):
                return mapping

        # If there are duplicate keys across mappings, raise a ValueError
        intersection = set().union(*all_keys)
        if len(intersection) < sum(len(keys) for keys in all_keys):
            raise ValueError(f"Duplicate keys found: {intersection}")

        # Return the combined mappings
        # ignore type because mypy doesn't follow all mappings being dicts
        return {**requester_mapping, **auth_options_mapping, **extra_mapping}  # type: ignore

    def _request_headers(
        self,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        extra_headers: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        Specifies request headers.
        Authentication headers will overwrite any overlapping headers returned from this method.
        """
        headers = self._get_request_options(
            stream_slice,
            next_page_token,
            self.get_request_headers,
            self.get_authenticator().get_auth_header,
            extra_headers,
        )
        if isinstance(headers, str):
            raise ValueError("Request headers cannot be a string")
        return {str(k): str(v) for k, v in headers.items()}

    def _request_params(
        self,
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        extra_params: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        Specifies the query parameters that should be set on an outgoing HTTP request given the inputs.

        E.g: you might want to define query parameters for paging if next_page_token is not None.
        """
        options = self._get_request_options(
            stream_slice, next_page_token, self.get_request_params, self.get_authenticator().get_request_params, extra_params
        )
        if isinstance(options, str):
            raise ValueError("Request params cannot be a string")
        return options

    def _request_body_data(
        self,
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        extra_body_data: Optional[Union[Mapping[str, Any], str]] = None,
    ) -> Optional[Union[Mapping[str, Any], str]]:
        """
        Specifies how to populate the body of the request with a non-JSON payload.

        If returns a ready text that it will be sent as is.
        If returns a dict that it will be converted to a urlencoded form.
        E.g. {"key1": "value1", "key2": "value2"} => "key1=value1&key2=value2"

        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        """
        # Warning: use self.state instead of the stream_state passed as argument!
        return self._get_request_options(
            stream_slice, next_page_token, self.get_request_body_data, self.get_authenticator().get_request_body_data, extra_body_data
        )

    def _request_body_json(
        self,
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        extra_body_json: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:
        """
        Specifies how to populate the body of the request with a JSON payload.

        At the same time only one of the 'request_body_data' and 'request_body_json' functions can be overridden.
        """
        # Warning: use self.state instead of the stream_state passed as argument!
        options = self._get_request_options(
            stream_slice, next_page_token, self.get_request_body_json, self.get_authenticator().get_request_body_json, extra_body_json
        )
        if isinstance(options, str):
            raise ValueError("Request body json cannot be a string")
        return options

    def _create_prepared_request(
        self,
        path: str,
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, Any]] = None,
        json: Any = None,
        data: Any = None,
    ) -> requests.PreparedRequest:
        http_method = str(self._http_method.value)
        args = {"method": http_method, "url": urljoin(self.get_url_base(), path), "headers": headers, "params": params}
        if http_method.upper() in BODY_REQUEST_METHODS:
            if json and data:
                raise RequestBodyException(
                    "At the same time only one of the 'request_body_data' and 'request_body_json' functions can return data"
                )
            elif json:
                args["json"] = json
            elif data:
                args["data"] = data

        return self._session.prepare_request(requests.Request(**args))

    def send_request(
        self,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        path: Optional[str] = None,
        request_headers: Optional[Mapping[str, Any]] = None,
        request_params: Optional[Mapping[str, Any]] = None,
        request_body_data: Optional[Union[Mapping[str, Any], str]] = None,
        request_body_json: Optional[Mapping[str, Any]] = None,
    ) -> Optional[requests.Response]:
        request = self._create_prepared_request(
            path=path if path is not None else self.get_path(stream_state=None, stream_slice=stream_slice, next_page_token=next_page_token),
            headers=self._request_headers(stream_slice, next_page_token, request_headers),
            params=self._request_params(stream_slice, next_page_token, request_params),
            json=self._request_body_json(stream_slice, next_page_token, request_body_json),
            data=self._request_body_data(stream_slice, next_page_token, request_body_data),
        )

        response = self._send_with_retry(request)
        return self._validate_response(response)

    def _send_with_retry(self, request: requests.PreparedRequest) -> requests.Response:
        """
        Creates backoff wrappers which are responsible for retry logic
        """

        """
        Backoff package has max_tries parameter that means total number of
        tries before giving up, so if this number is 0 no calls expected to be done.
        But for this class we call it max_REtries assuming there would be at
        least one attempt and some retry attempts, to comply this logic we add
        1 to expected retries attempts.
        """
        max_tries = self.max_retries
        """
        According to backoff max_tries docstring:
            max_tries: The maximum number of attempts to make before giving
                up ...The default value of None means there is no limit to
                the number of tries.
        This implies that if max_tries is explicitly set to None there is no
        limit to retry attempts, otherwise it is limited number of tries. But
        this is not true for current version of backoff packages (1.8.0). Setting
        max_tries to 0 or negative number would result in endless retry attempts.
        Add this condition to avoid an endless loop if it hasn't been set
        explicitly (i.e. max_retries is not None).
        """
        if max_tries is not None:
            max_tries = max(0, max_tries) + 1

        user_backoff_handler = user_defined_backoff_handler(max_tries=max_tries)(self._send)
        backoff_handler = default_backoff_handler(max_tries=max_tries, factor=self._DEFAULT_RETRY_FACTOR)
        # backoff handlers wrap _send, so it will always return a response
        return backoff_handler(user_backoff_handler)(request)  # type: ignore

    def _send(self, request: requests.PreparedRequest) -> requests.Response:
        """
        Wraps sending the request in rate limit and error handlers.
        Please note that error handling for HTTP status codes will be ignored if raise_on_http_errors is set to False

        This method handles two types of exceptions:
            1. Expected transient exceptions e.g: 429 status code.
            2. Unexpected transient exceptions e.g: timeout.

        To trigger a backoff, we raise an exception that is handled by the backoff decorator. If an exception is not handled by the decorator will
        fail the sync.

        For expected transient exceptions, backoff time is determined by the type of exception raised:
            1. CustomBackoffException uses the user-provided backoff value
            2. DefaultBackoffException falls back on the decorator's default behavior e.g: exponential backoff

        Unexpected transient exceptions use the default backoff parameters.
        Unexpected persistent exceptions are not handled and will cause the sync to fail.
        """
        self.logger.debug(
            "Making outbound API request", extra={"headers": request.headers, "url": request.url, "request_body": request.body}
        )
        response: requests.Response = self._session.send(request)
        self.logger.debug("Receiving response", extra={"headers": response.headers, "status": response.status_code, "body": response.text})
        if self._should_retry(response):
            custom_backoff_time = self._backoff_time(response)
            if custom_backoff_time:
                raise UserDefinedBackoffException(backoff=custom_backoff_time, request=request, response=response)
            else:
                raise DefaultBackoffException(request=request, response=response)
        return response

    def _validate_response(
        self,
        response: requests.Response,
    ) -> Optional[requests.Response]:
        # if fail -> raise exception
        # if ignore -> ignore response and return None
        # else -> delegate to caller
        if self.error_handler is None:
            return response

        response_status = self.interpret_response_status(response)
        if response_status.action == ResponseAction.FAIL:
            error_message = (
                response_status.error_message
                or f"Request to {response.request.url} failed with status code {response.status_code} and error message {HttpRequester.parse_response_error_message(response)}"
            )
            raise ReadException(error_message)
        elif response_status.action == ResponseAction.IGNORE:
            self.logger.info(
                f"Ignoring response for failed request with error message {HttpRequester.parse_response_error_message(response)}"
            )

        return response

    @classmethod
    def parse_response_error_message(cls, response: requests.Response) -> Optional[str]:
        """
        Parses the raw response object from a failed request into a user-friendly error message.
        By default, this method tries to grab the error message from JSON responses by following common API patterns. Override to parse differently.

        :param response:
        :return: A user-friendly message that indicates the cause of the error
        """

        # default logic to grab error from common fields
        def _try_get_error(value: Any) -> Any:
            if isinstance(value, str):
                return value
            elif isinstance(value, list):
                return ", ".join(_try_get_error(v) for v in value)
            elif isinstance(value, dict):
                new_value = (
                    value.get("message")
                    or value.get("messages")
                    or value.get("error")
                    or value.get("errors")
                    or value.get("failures")
                    or value.get("failure")
                )
                return _try_get_error(new_value)
            return None

        try:
            body = response.json()
            error = _try_get_error(body)
            return str(error) if error else None
        except requests.exceptions.JSONDecodeError:
            return None
