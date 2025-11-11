#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import InitVar, dataclass, field
from typing import Any, Callable, Mapping, MutableMapping, Optional, Union
from urllib.parse import urljoin

import requests

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import (
    DeclarativeAuthenticator,
    NoAuth,
)
from airbyte_cdk.sources.declarative.decoders import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import (
    InterpolatedString,
)
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod, Requester
from airbyte_cdk.sources.message import MessageRepository, NoopMessageRepository
from airbyte_cdk.sources.streams.call_rate import APIBudget
from airbyte_cdk.sources.streams.http import HttpClient
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler
from airbyte_cdk.sources.types import Config, EmptyString, StreamSlice, StreamState
from airbyte_cdk.utils.mapping_helpers import (
    combine_mappings,
    get_interpolation_context,
)


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
        backoff_strategies (Optional[List[BackoffStrategy]]): List of backoff strategies to use when retrying requests
        config (Config): The user-provided configuration as specified by the source's spec
        use_cache (bool): Indicates that data should be cached for this stream
    """

    name: str
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    url: Optional[Union[InterpolatedString, str]] = None
    url_base: Optional[Union[InterpolatedString, str]] = None
    path: Optional[Union[InterpolatedString, str]] = None
    authenticator: Optional[DeclarativeAuthenticator] = None
    http_method: Union[str, HttpMethod] = HttpMethod.GET
    request_options_provider: Optional[InterpolatedRequestOptionsProvider] = None
    error_handler: Optional[ErrorHandler] = None
    api_budget: Optional[APIBudget] = None
    disable_retries: bool = False
    message_repository: MessageRepository = NoopMessageRepository()
    use_cache: bool = False
    _exit_on_rate_limit: bool = False
    stream_response: bool = False
    decoder: Decoder = field(default_factory=lambda: JsonDecoder(parameters={}))

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._url = InterpolatedString.create(
            self.url if self.url else EmptyString, parameters=parameters
        )
        # deprecated
        self._url_base = InterpolatedString.create(
            self.url_base if self.url_base else EmptyString, parameters=parameters
        )
        # deprecated
        self._path = InterpolatedString.create(
            self.path if self.path else EmptyString, parameters=parameters
        )
        if self.request_options_provider is None:
            self._request_options_provider = InterpolatedRequestOptionsProvider(
                config=self.config, parameters=parameters
            )
        elif isinstance(self.request_options_provider, dict):
            self._request_options_provider = InterpolatedRequestOptionsProvider(
                config=self.config, **self.request_options_provider
            )
        else:
            self._request_options_provider = self.request_options_provider
        self._authenticator = self.authenticator or NoAuth(parameters=parameters)
        self._http_method = (
            HttpMethod[self.http_method] if isinstance(self.http_method, str) else self.http_method
        )
        self.error_handler = self.error_handler
        self._parameters = parameters

        if self.error_handler is not None and hasattr(self.error_handler, "backoff_strategies"):
            backoff_strategies = self.error_handler.backoff_strategies  # type: ignore
        else:
            backoff_strategies = None

        self._http_client = HttpClient(
            name=self.name,
            logger=self.logger,
            error_handler=self.error_handler,
            api_budget=self.api_budget,
            authenticator=self._authenticator,
            use_cache=self.use_cache,
            backoff_strategy=backoff_strategies,
            disable_retries=self.disable_retries,
            message_repository=self.message_repository,
        )

    @property
    def exit_on_rate_limit(self) -> bool:
        return self._exit_on_rate_limit

    @exit_on_rate_limit.setter
    def exit_on_rate_limit(self, value: bool) -> None:
        self._exit_on_rate_limit = value

    def get_authenticator(self) -> DeclarativeAuthenticator:
        return self._authenticator

    def get_url(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        interpolation_context = get_interpolation_context(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

        return str(self._url.eval(self.config, **interpolation_context))

    def _get_url(
        self,
        *,
        path: Optional[str] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        url = self.get_url(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

        url_base = self.get_url_base(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

        path = path or self.get_path(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

        full_url = (
            self._join_url(url_base, path)
            if url_base
            else self._join_url(url, path)
            if path
            else url
        )

        return full_url

    def get_url_base(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        interpolation_context = get_interpolation_context(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )
        return str(self._url_base.eval(self.config, **interpolation_context))

    def get_path(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        interpolation_context = get_interpolation_context(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )
        path = str(self._path.eval(self.config, **interpolation_context))
        return path.lstrip("/")

    def get_method(self) -> HttpMethod:
        return self._http_method

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return self._request_options_provider.get_request_params(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return self._request_options_provider.get_request_headers(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
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
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
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
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(f"airbyte.HttpRequester.{self.name}")

    def _get_request_options(
        self,
        stream_state: Optional[StreamState],
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

        is_body_json = requester_method.__name__ == "get_request_body_json"

        return combine_mappings(
            [
                requester_method(
                    stream_state=stream_state,
                    stream_slice=stream_slice,
                    next_page_token=next_page_token,
                ),
                auth_options_method(),
                extra_options,
            ],
            allow_same_value_merge=is_body_json,
        )

    def _request_headers(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        extra_headers: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        Specifies request headers.
        Authentication headers will overwrite any overlapping headers returned from this method.
        """
        headers = self._get_request_options(
            stream_state,
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
        stream_state: Optional[StreamState],
        stream_slice: Optional[StreamSlice],
        next_page_token: Optional[Mapping[str, Any]],
        extra_params: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        Specifies the query parameters that should be set on an outgoing HTTP request given the inputs.

        E.g: you might want to define query parameters for paging if next_page_token is not None.
        """
        options = self._get_request_options(
            stream_state,
            stream_slice,
            next_page_token,
            self.get_request_params,
            self.get_authenticator().get_request_params,
            extra_params,
        )
        if isinstance(options, str):
            raise ValueError("Request params cannot be a string")

        for k, v in options.items():
            if isinstance(v, (dict,)):
                raise ValueError(
                    f"Invalid value for `{k}` parameter. The values of request params cannot be an object."
                )

        return options

    def _request_body_data(
        self,
        stream_state: Optional[StreamState],
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
            stream_state,
            stream_slice,
            next_page_token,
            self.get_request_body_data,
            self.get_authenticator().get_request_body_data,
            extra_body_data,
        )

    def _request_body_json(
        self,
        stream_state: Optional[StreamState],
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
            stream_state,
            stream_slice,
            next_page_token,
            self.get_request_body_json,
            self.get_authenticator().get_request_body_json,
            extra_body_json,
        )
        if isinstance(options, str):
            raise ValueError("Request body json cannot be a string")
        return options

    @classmethod
    def _join_url(cls, url_base: str, path: Optional[str] = None) -> str:
        """
        Joins a base URL with a given path and returns the resulting URL with any trailing slash removed.

        This method ensures that there are no duplicate slashes when concatenating the base URL and the path,
        which is useful when the full URL is provided from an interpolation context.

        Args:
            url_base (str): The base URL to which the path will be appended.
            path (Optional[str]): The path to join with the base URL.

        Returns:
            str: The resulting joined URL.

        Note:
            Related issue: https://github.com/airbytehq/airbyte-internal-issues/issues/11869
            - If the path is an empty string or None, the method returns the base URL with any trailing slash removed.

        Example:
            1) _join_url("https://example.com/api/", "endpoint") >> 'https://example.com/api/endpoint'
            2) _join_url("https://example.com/api", "/endpoint") >> 'https://example.com/api/endpoint'
            3) _join_url("https://example.com/api/", "") >> 'https://example.com/api/'
            4) _join_url("https://example.com/api", None) >> 'https://example.com/api'
        """

        # return a full-url if provided directly from interpolation context
        if path == EmptyString or path is None:
            return url_base
        else:
            # since we didn't provide a full-url, the url_base might not have a trailing slash
            # so we join the url_base and path correctly
            if not url_base.endswith("/"):
                url_base += "/"

        return urljoin(url_base, path)

    def send_request(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        path: Optional[str] = None,
        request_headers: Optional[Mapping[str, Any]] = None,
        request_params: Optional[Mapping[str, Any]] = None,
        request_body_data: Optional[Union[Mapping[str, Any], str]] = None,
        request_body_json: Optional[Mapping[str, Any]] = None,
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
    ) -> Optional[requests.Response]:
        request, response = self._http_client.send_request(
            http_method=self.get_method().value,
            url=self._get_url(
                path=path,
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
            ),
            request_kwargs={"stream": self.stream_response},
            headers=self._request_headers(
                stream_state, stream_slice, next_page_token, request_headers
            ),
            params=self._request_params(
                stream_state, stream_slice, next_page_token, request_params
            ),
            json=self._request_body_json(
                stream_state, stream_slice, next_page_token, request_body_json
            ),
            data=self._request_body_data(
                stream_state, stream_slice, next_page_token, request_body_data
            ),
            dedupe_query_params=True,
            log_formatter=log_formatter,
            exit_on_rate_limit=self._exit_on_rate_limit,
        )

        return response
