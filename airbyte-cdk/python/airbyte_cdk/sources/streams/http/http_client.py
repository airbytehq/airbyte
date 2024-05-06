#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
import urllib
from pathlib import Path
from typing import Any, Mapping, Optional, Tuple, Union, List

import requests
import requests_cache
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.http_config import MAX_CONNECTION_POOL_SIZE
from airbyte_cdk.sources.streams.call_rate import APIBudget, CachedLimiterSession, LimiterSession
from airbyte_cdk.utils.constants import ENV_REQUEST_CACHE_PATH
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from requests.auth import AuthBase

from .decoders import Decoder, JsonDecoder
from .error_handlers import DefaultBackoffStrategy, HttpStatusErrorHandler, JsonErrorMessageParser, ResponseAction, ErrorHandler
from .exceptions import DefaultBackoffException, RequestBodyException, UserDefinedBackoffException
from .rate_limiting import default_backoff_handler, user_defined_backoff_handler

BODY_REQUEST_METHODS = ("GET", "POST", "PUT", "PATCH")


class NoopDecoder(Decoder):
    def decode(self, response: requests.Response) -> Union[Mapping[str, Any], List]:
        pass

    def validate_response(self, response: requests.Response) -> None:
        pass


class HttpClient:
    def __init__(
        self,
        stream_name: str,
        logger: logging.Logger,
        error_handler: Optional[ErrorHandler] = None,
        api_budget: Optional[APIBudget] = None,
        session: Optional[Union[requests.Session, requests_cache.CachedSession]] = None,
        authenticator: Optional[AuthBase] = None,
    ):
        self._stream_name = stream_name
        self._api_budget: APIBudget = api_budget or APIBudget(policies=[])
        if session:
            self._session = session
        else:
            self._session = self.request_session()
            self._session.mount(
                "https://", requests.adapters.HTTPAdapter(pool_connections=MAX_CONNECTION_POOL_SIZE, pool_maxsize=MAX_CONNECTION_POOL_SIZE)
            )
        if isinstance(authenticator, AuthBase):
            self._session.auth = authenticator
        self._logger = logger
        self._error_handler = error_handler or HttpStatusErrorHandler(logger)
        self._backoff_strategy = DefaultBackoffStrategy()
        self._response_decoder = NoopDecoder()
        self._error_message_parser = JsonErrorMessageParser()

    # property moved from HttpStream
    @property
    def cache_filename(self) -> str:
        """
        Override if needed. Return the name of cache file
        Note that if the environment variable REQUEST_CACHE_PATH is not set, the cache will be in-memory only.
        """
        return f"{self._stream_name}.sqlite"

    # property moved from HttpStream
    @property
    def use_cache(self) -> bool:
        """
        Override if needed. If True, all records will be cached.
        Note that if the environment variable REQUEST_CACHE_PATH is not set, the cache will be in-memory only.
        """
        return False

    # public moved method from HttpStream
    def request_session(self) -> requests.Session:
        """
        Session factory based on use_cache property and call rate limits (api_budget parameter)
        :return: instance of request-based session
        """
        if self.use_cache:
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

    # public moved method from HttpStream
    def clear_cache(self) -> None:
        """
        Clear cached requests for current session, can be called any time
        """
        if isinstance(self._session, CachedLimiterSession):
            self._session.cache.clear()  # type: ignore # cache.clear is not typed

    # private method moved from HttpStream
    def _dedupe_query_params(self, url: str, params: Mapping[str, str]) -> Mapping[str, str]:
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

    # private method moved from HttpStream
    def _create_prepared_request(
        self,
        http_method: str,
        url: str,
        dedupe_query_params: bool = True,
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, str]] = None,
        json: Optional[Mapping[str, Any]] = None,
        data: Optional[Union[str, Mapping[str, Any]]] = None,
    ):
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

    def _send_with_retry(self, request: requests.PreparedRequest, request_kwargs: Optional[Mapping[str, Any]] = None) -> requests.Response:
        """
        Backoff package has max_tries parameter that means total number of
        tries before giving up, so if this number is 0 no calls expected to be done.
        But for this class we call it max_REtries assuming there would be at
        least one attempt and some retry attempts, to comply this logic we add
        1 to expected retries attempts.
        """
        if self._backoff_strategy.max_retries is not None:
            max_tries = max(0, self._backoff_strategy.max_retries) + 1

        user_backoff_handler = user_defined_backoff_handler(max_tries=max_tries, max_time=self._backoff_strategy.max_time)(self._send)
        backoff_handler = default_backoff_handler(
            max_tries=max_tries, max_time=self._backoff_strategy.max_time, factor=self._backoff_strategy.retry_factor
        )
        # backoff handlers wrap _send, so it will always return a response
        response = backoff_handler(user_backoff_handler)(request, request_kwargs)

        return response

    def _send(self, request: requests.PreparedRequest, request_kwargs: Optional[Mapping[str, Any]] = None) -> requests.Response:

        self._logger.debug(
            "Making outbound API request", extra={"headers": request.headers, "url": request.url, "request_body": request.body}
        )

        if request_kwargs is None:
            request_kwargs = {}

        try:
            response: requests.Response = self._session.send(request, **request_kwargs)
            self._response_decoder.validate_response(response)
        except requests.RequestException as exc:
            response_action = ResponseAction.RETRY
            failure_type = FailureType.transient_error
            response_error_message = f"Request to {request.url} failed with exception: {exc}"
            self._logger.debug(response_error_message)
            exc = exc
            response = None
        else:
            response_action, failure_type, response_error_message = self._error_handler.interpret_response(response=response)
            exc = None

        # Evaluation of response.text can be heavy, for example, if streaming a large response
        # Do it only in debug mode
        if response is not None:
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug(
                    "Receiving response", extra={"headers": response.headers, "status": response.status_code, "body": response.text}
                )

            if response_action == ResponseAction.FAIL:
                error_message = (
                    f"Request failed to {request.url} with error {exc}"
                    if exc
                    else response_error_message
                    or f"Request to {response.request.url} failed with status code {response.status_code} and error message {self._error_message_parser.parse_response_error_message(response)}"
                )
                # TODO: Provide better internal/external error messaging
                raise AirbyteTracedException(
                    internal_message=error_message,
                    message=error_message,
                    failure_type=failure_type,
                )

            if response_action == ResponseAction.IGNORE:
                self._logger.info(
                    f"Ignoring response with status code {response.status_code} for request to {request.url}"
                    if response
                    else f"Ignoring response for request to {request.url} with error {exc}"
                )

        # TODO: Consider dynamic retry count depending on subsequent error codes
        if response_action == ResponseAction.RETRY:
            custom_backoff_time = self._backoff_strategy.backoff_time(response)
            error_message = response_error_message
            if custom_backoff_time:
                raise UserDefinedBackoffException(
                    backoff=custom_backoff_time, request=request, response=response, error_message=error_message
                )
            else:
                raise DefaultBackoffException(request=request, response=response, error_message=error_message)

        if not response_action:
            # Raise any HTTP exceptions that happened in case there were unexpected ones
            try:
                response.raise_for_status()
            except requests.HTTPError as exc:
                self._logger.error(response.text)
                raise exc

        return response

    def send_request(
        self,
        http_method: str,
        url: str,
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, str]] = None,
        json: Optional[Mapping[str, Any]] = None,
        data: Optional[Union[str, Mapping[str, Any]]] = None,
        dedupe_query_params: bool = False,
        request_kwargs: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[requests.PreparedRequest, requests.Response]:
        """
        Prepares and sends request and return request and response objects.
        """

        request: requests.PreparedRequest = self._create_prepared_request(
            http_method=http_method, url=url, dedupe_query_params=dedupe_query_params, headers=headers, params=params, json=json, data=data
        )

        response: requests.Response = self._send_with_retry(request=request, request_kwargs=request_kwargs)

        return request, response
