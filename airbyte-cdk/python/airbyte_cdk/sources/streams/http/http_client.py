#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
import urllib
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple, Union

import requests
import requests_cache
from airbyte_cdk.models import Level
from airbyte_cdk.sources.http_config import MAX_CONNECTION_POOL_SIZE
from airbyte_cdk.sources.message import MessageRepository
from airbyte_cdk.sources.streams.call_rate import APIBudget, CachedLimiterSession, LimiterSession
from airbyte_cdk.sources.streams.http.error_handlers import (
    BackoffStrategy,
    DefaultBackoffStrategy,
    ErrorHandler,
    ErrorMessageParser,
    ErrorResolution,
    HttpStatusErrorHandler,
    JsonErrorMessageParser,
    ResponseAction,
)
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, RequestBodyException, UserDefinedBackoffException
from airbyte_cdk.sources.streams.http.rate_limiting import http_client_default_backoff_handler, user_defined_backoff_handler
from airbyte_cdk.utils.constants import ENV_REQUEST_CACHE_PATH
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from requests.auth import AuthBase

BODY_REQUEST_METHODS = ("GET", "POST", "PUT", "PATCH")


class HttpClient:

    _DEFAULT_MAX_RETRY: int = 5
    _DEFAULT_MAX_TIME: int = 60 * 10

    def __init__(
        self,
        name: str,
        logger: logging.Logger,
        error_handler: Optional[ErrorHandler] = None,
        api_budget: Optional[APIBudget] = None,
        session: Optional[Union[requests.Session, requests_cache.CachedSession]] = None,
        authenticator: Optional[AuthBase] = None,
        use_cache: bool = False,
        backoff_strategy: Optional[Union[BackoffStrategy, List[BackoffStrategy]]] = None,
        error_message_parser: Optional[ErrorMessageParser] = None,
        disable_retries: bool = False,
        message_respository: Optional[MessageRepository] = None,
    ):
        self._name = name
        self._api_budget: APIBudget = api_budget or APIBudget(policies=[])
        if session:
            self._session = session
        else:
            self._use_cache = use_cache
            self._session = self._request_session()
            self._session.mount(
                "https://", requests.adapters.HTTPAdapter(pool_connections=MAX_CONNECTION_POOL_SIZE, pool_maxsize=MAX_CONNECTION_POOL_SIZE)
            )
        if isinstance(authenticator, AuthBase):
            self._session.auth = authenticator
        self._logger = logger
        self._error_handler = error_handler or HttpStatusErrorHandler(self._logger)
        if backoff_strategy is not None:
            if isinstance(backoff_strategy, list):
                self._backoff_strategies = backoff_strategy
            else:
                self._backoff_strategies = [backoff_strategy]
        else:
            self._backoff_strategies = [DefaultBackoffStrategy()]
        self._error_message_parser = error_message_parser or JsonErrorMessageParser()
        self._request_attempt_count: Dict[requests.PreparedRequest, int] = {}
        self._disable_retries = disable_retries
        self._message_repository = message_respository

    @property
    def cache_filename(self) -> str:
        """
        Override if needed. Return the name of cache file
        Note that if the environment variable REQUEST_CACHE_PATH is not set, the cache will be in-memory only.
        """
        return f"{self._name}.sqlite"

    def _request_session(self) -> requests.Session:
        """
        Session factory based on use_cache property and call rate limits (api_budget parameter)
        :return: instance of request-based session
        """
        if self._use_cache:
            cache_dir = os.getenv(ENV_REQUEST_CACHE_PATH)
            # Use in-memory cache if cache_dir is not set
            # This is a non-obvious interface, but it ensures we don't write sql files when running unit tests
            if cache_dir:
                sqlite_path = str(Path(cache_dir) / self.cache_filename)
            else:
                sqlite_path = "file::memory:?cache=shared"
            return CachedLimiterSession(sqlite_path, backend="sqlite", api_budget=self._api_budget)  # type: ignore # there are no typeshed stubs for requests_cache
        else:
            return LimiterSession(api_budget=self._api_budget)

    def _dedupe_query_params(self, url: str, params: Optional[Mapping[str, str]]) -> Mapping[str, str]:
        """
        Remove query parameters from params mapping if they are already encoded in the URL.
        :param url: URL with
        :param params:
        :return:
        """
        if params is None:
            params = {}
        query_string = urllib.parse.urlparse(url).query
        query_dict = {k: v[0] for k, v in urllib.parse.parse_qs(query_string).items()}

        duplicate_keys_with_same_value = {k for k in query_dict.keys() if str(params.get(k)) == str(query_dict[k])}
        return {k: v for k, v in params.items() if k not in duplicate_keys_with_same_value}

    def _create_prepared_request(
        self,
        http_method: str,
        url: str,
        dedupe_query_params: bool = False,
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, str]] = None,
        json: Optional[Mapping[str, Any]] = None,
        data: Optional[Union[str, Mapping[str, Any]]] = None,
    ) -> requests.PreparedRequest:
        if dedupe_query_params:
            query_params = self._dedupe_query_params(url, params)
        else:
            query_params = params or {}
        args = {"method": http_method, "url": url, "headers": headers, "params": query_params}
        if http_method.upper() in BODY_REQUEST_METHODS:
            if json and data:
                raise RequestBodyException(
                    "At the same time only one of the 'request_body_data' and 'request_body_json' functions can return data"
                )
            elif json:
                args["json"] = json
            elif data:
                args["data"] = data
        prepared_request: requests.PreparedRequest = self._session.prepare_request(requests.Request(**args))

        return prepared_request

    @property
    def _max_retries(self) -> int:
        """
        Determines the max retries based on the provided error handler.
        """
        max_retries = None
        if self._disable_retries:
            max_retries = 0
        else:
            max_retries = self._error_handler.max_retries
        return max_retries if max_retries is not None else self._DEFAULT_MAX_RETRY

    @property
    def _max_time(self) -> int:
        """
        Determines the max time based on the provided error handler.
        """
        return self._error_handler.max_time if self._error_handler.max_time is not None else self._DEFAULT_MAX_TIME

    def _send_with_retry(
        self,
        request: requests.PreparedRequest,
        request_kwargs: Mapping[str, Any],
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
    ) -> requests.Response:
        """
        Sends a request with retry logic.

        Args:
            request (requests.PreparedRequest): The prepared HTTP request to send.
            request_kwargs (Mapping[str, Any]): Additional keyword arguments for the request.

        Returns:
            requests.Response: The HTTP response received from the server after retries.
        """

        max_retries = self._max_retries
        max_tries = max(0, max_retries) + 1
        max_time = self._max_time

        user_backoff_handler = user_defined_backoff_handler(max_tries=max_tries, max_time=max_time)(self._send)
        backoff_handler = http_client_default_backoff_handler(max_tries=max_tries, max_time=max_time)
        # backoff handlers wrap _send, so it will always return a response
        response = backoff_handler(user_backoff_handler)(request, request_kwargs, log_formatter=log_formatter)  # type: ignore # mypy can't infer that backoff_handler wraps _send

        return response

    def _send(
        self,
        request: requests.PreparedRequest,
        request_kwargs: Mapping[str, Any],
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
    ) -> requests.Response:

        if request not in self._request_attempt_count:
            self._request_attempt_count[request] = 1
        else:
            self._request_attempt_count[request] += 1

        self._logger.debug(
            "Making outbound API request", extra={"headers": request.headers, "url": request.url, "request_body": request.body}
        )

        response: Optional[requests.Response] = None
        exc: Optional[requests.RequestException] = None

        try:
            response = self._session.send(request, **request_kwargs)
        except requests.RequestException as e:
            exc = e

        error_resolution: ErrorResolution = self._error_handler.interpret_response(response if response is not None else exc)

        # Evaluation of response.text can be heavy, for example, if streaming a large response
        # Do it only in debug mode
        if self._logger.isEnabledFor(logging.DEBUG) and response is not None:
            self._logger.debug(
                "Receiving response", extra={"headers": response.headers, "status": response.status_code, "body": response.text}
            )

        # Request/repsonse logging for declarative cdk.
        if log_formatter is not None and response is not None and self._message_repository is not None:
            formatter = log_formatter
            self._message_repository.log_message(
                Level.DEBUG,
                lambda: formatter(response),  # type: ignore # log_formatter is always cast to a callable
            )

        if error_resolution.response_action == ResponseAction.FAIL:
            if response:
                error_message = f"'{request.method}' request to '{request.url}' failed with status code '{response.status_code}' and error message '{self._error_message_parser.parse_response_error_message(response)}'"
            else:
                error_message = f"'{request.method}' request to '{request.url}' failed with exception: '{exc}'"

            raise AirbyteTracedException(
                internal_message=error_message,
                message=error_resolution.error_message or error_message,
                failure_type=error_resolution.failure_type,
            )

        elif error_resolution.response_action == ResponseAction.IGNORE:
            if response:
                log_message = (
                    f"Ignoring response for '{request.method}' request to '{request.url}' with response code '{response.status_code}'"
                )
            else:
                log_message = f"Ignoring response for '{request.method}' request to '{request.url}' with error '{exc}'"

            self._logger.info(error_resolution.error_message or log_message)

        # TODO: Consider dynamic retry count depending on subsequent error codes
        elif error_resolution.response_action == ResponseAction.RETRY:
            user_defined_backoff_time = None
            for backoff_strategy in self._backoff_strategies:
                backoff_time = backoff_strategy.backoff_time(
                    response_or_exception=response if response is not None else exc, attempt_count=self._request_attempt_count[request]
                )
                if backoff_time:
                    user_defined_backoff_time = backoff_time
                    break
            error_message = (
                error_resolution.error_message
                or f"Request to {request.url} failed with failure type {error_resolution.failure_type}, response action {error_resolution.response_action}."
            )
            if user_defined_backoff_time:
                raise UserDefinedBackoffException(
                    backoff=user_defined_backoff_time,
                    request=request,
                    response=(response if response is not None else exc),
                    error_message=error_message,
                )
            else:
                raise DefaultBackoffException(
                    request=request, response=(response if response is not None else exc), error_message=error_message
                )

        elif response:
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                self._logger.error(response.text)
                raise e

        return response  # type: ignore # will either return a valid response of type requests.Response or raise an exception

    def send_request(
        self,
        http_method: str,
        url: str,
        request_kwargs: Mapping[str, Any],
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, str]] = None,
        json: Optional[Mapping[str, Any]] = None,
        data: Optional[Union[str, Mapping[str, Any]]] = None,
        dedupe_query_params: bool = False,
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
    ) -> Tuple[requests.PreparedRequest, requests.Response]:
        """
        Prepares and sends request and return request and response objects.
        """

        request: requests.PreparedRequest = self._create_prepared_request(
            http_method=http_method, url=url, dedupe_query_params=dedupe_query_params, headers=headers, params=params, json=json, data=data
        )

        response: requests.Response = self._send_with_retry(request=request, request_kwargs=request_kwargs, log_formatter=log_formatter)

        return request, response
