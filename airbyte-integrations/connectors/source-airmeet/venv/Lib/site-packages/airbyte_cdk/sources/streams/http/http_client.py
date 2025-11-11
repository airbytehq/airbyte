#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
import urllib
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple, Union

import orjson
import requests
import requests_cache
from requests.auth import AuthBase

from airbyte_cdk.models import (
    AirbyteMessageSerializer,
    AirbyteStreamStatus,
    AirbyteStreamStatusReason,
    AirbyteStreamStatusReasonType,
    FailureType,
    Level,
    StreamDescriptor,
)
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
from airbyte_cdk.sources.streams.http.exceptions import (
    BaseBackoffException,
    DefaultBackoffException,
    RateLimitBackoffException,
    RequestBodyException,
    UserDefinedBackoffException,
)
from airbyte_cdk.sources.streams.http.pagination_reset_exception import (
    PaginationResetRequiredException,
)
from airbyte_cdk.sources.streams.http.rate_limiting import (
    http_client_default_backoff_handler,
    rate_limit_default_backoff_handler,
    user_defined_backoff_handler,
)
from airbyte_cdk.sources.utils.types import JsonType
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets
from airbyte_cdk.utils.constants import ENV_REQUEST_CACHE_PATH
from airbyte_cdk.utils.stream_status_utils import (
    as_airbyte_message as stream_status_as_airbyte_message,
)
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

BODY_REQUEST_METHODS = ("GET", "POST", "PUT", "PATCH")


def monkey_patched_get_item(self, key):  # type: ignore # this interface is a copy/paste from the requests_cache lib
    """
    con.execute can lead to `sqlite3.InterfaceError: bad parameter or other API misuse`. There was a fix implemented
    [here](https://github.com/requests-cache/requests-cache/commit/5ca6b9cdcb2797dd2fed485872110ccd72aee55d#diff-f43db4a5edf931647c32dec28ea7557aae4cae8444af4b26c8ecbe88d8c925aaL330-R332)
    but there is still no official releases of requests_cache that this is part of. Hence, we will monkeypatch it for now.
    """
    with self.connection() as con:
        # Using placeholders here with python 3.12+ and concurrency results in the error:
        # sqlite3.InterfaceError: bad parameter or other API misuse
        cur = con.execute(f"SELECT value FROM {self.table_name} WHERE key='{key}'")
        row = cur.fetchone()
        cur.close()
        if not row:
            raise KeyError(key)

        return self.deserialize(key, row[0])


requests_cache.SQLiteDict.__getitem__ = monkey_patched_get_item  # type: ignore # see the method doc for more information


class MessageRepresentationAirbyteTracedErrors(AirbyteTracedException):
    """
    Before the migration to the HttpClient in low-code, the exception raised was
    [ReadException](https://github.com/airbytehq/airbyte/blob/8fdd9818ec16e653ba3dd2b167a74b7c07459861/airbyte-cdk/python/airbyte_cdk/sources/declarative/requesters/http_requester.py#L566).
    This has been moved to a AirbyteTracedException. The printing on this is questionable (AirbyteTracedException string representation
    shows the internal_message and not the message). We have already discussed moving the AirbyteTracedException string representation to
    `message` but the impact is unclear and hard to quantify so we will do it here only for now.
    """

    def __str__(self) -> str:
        if self.message:
            return self.message
        elif self.internal_message:
            return self.internal_message
        return ""


class HttpClient:
    _DEFAULT_MAX_RETRY: int = 5
    _DEFAULT_MAX_TIME: int = 60 * 10
    _ACTIONS_TO_RETRY_ON = {ResponseAction.RETRY, ResponseAction.RATE_LIMITED}

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
        message_repository: Optional[MessageRepository] = None,
    ):
        self._name = name
        self._api_budget: APIBudget = api_budget or APIBudget(policies=[])
        if session:
            self._session = session
        else:
            self._use_cache = use_cache
            self._session = self._request_session()
            self._session.mount(
                "https://",
                requests.adapters.HTTPAdapter(
                    pool_connections=MAX_CONNECTION_POOL_SIZE, pool_maxsize=MAX_CONNECTION_POOL_SIZE
                ),
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
        self._message_repository = message_repository

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
            # Use in-memory cache if cache_dir is not set
            # This is a non-obvious interface, but it ensures we don't write sql files when running unit tests
            sqlite_path = (
                str(Path(cache_dir) / self.cache_filename)
                if cache_dir
                else "file::memory:?cache=shared"
            )
            # By using `PRAGMA synchronous=OFF` and `PRAGMA journal_mode=WAL`, we reduce the possible occurrences of `database table is locked` errors.
            # Note that those were blindly added at the same time and one or the other might be sufficient to prevent the issues but we have seen good results with both. Feel free to revisit given more information.
            # There are strong signals that `fast_save` might create problems but if the sync crashes, we start back from the beginning in terms of sqlite anyway so the impact should be minimal. Signals are:
            # * https://github.com/requests-cache/requests-cache/commit/7fa89ffda300331c37d8fad7f773348a3b5b0236#diff-f43db4a5edf931647c32dec28ea7557aae4cae8444af4b26c8ecbe88d8c925aaR238
            # * https://github.com/requests-cache/requests-cache/commit/7fa89ffda300331c37d8fad7f773348a3b5b0236#diff-2e7f95b7d7be270ff1a8118f817ea3e6663cdad273592e536a116c24e6d23c18R164-R168
            # * `If the application running SQLite crashes, the data will be safe, but the database [might become corrupted](https://www.sqlite.org/howtocorrupt.html#cfgerr) if the operating system crashes or the computer loses power before that data has been written to the disk surface.` in [this description](https://www.sqlite.org/pragma.html#pragma_synchronous).
            backend = requests_cache.SQLiteCache(sqlite_path, fast_save=True, wal=True)
            return CachedLimiterSession(
                cache_name=sqlite_path,
                backend=backend,
                api_budget=self._api_budget,
                match_headers=True,
            )
        else:
            return LimiterSession(api_budget=self._api_budget)

    def clear_cache(self) -> None:
        """
        Clear cached requests for current session, can be called any time
        """
        if isinstance(self._session, requests_cache.CachedSession):
            self._session.cache.clear()  # type: ignore # cache.clear is not typed

    def _dedupe_query_params(
        self, url: str, params: Optional[Mapping[str, str]]
    ) -> Mapping[str, str]:
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

        duplicate_keys_with_same_value = {
            k for k in query_dict.keys() if str(params.get(k)) == str(query_dict[k])
        }
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
        prepared_request: requests.PreparedRequest = self._session.prepare_request(
            requests.Request(**args)
        )

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
        return (
            self._error_handler.max_time
            if self._error_handler.max_time is not None
            else self._DEFAULT_MAX_TIME
        )

    def _send_with_retry(
        self,
        request: requests.PreparedRequest,
        request_kwargs: Mapping[str, Any],
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
        exit_on_rate_limit: Optional[bool] = False,
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

        user_backoff_handler = user_defined_backoff_handler(max_tries=max_tries, max_time=max_time)(
            self._send
        )
        rate_limit_backoff_handler = rate_limit_default_backoff_handler(max_tries=max_tries)
        backoff_handler = http_client_default_backoff_handler(
            max_tries=max_tries, max_time=max_time
        )
        # backoff handlers wrap _send, so it will always return a response -- except when all retries are exhausted
        try:
            response = backoff_handler(rate_limit_backoff_handler(user_backoff_handler))(
                request,
                request_kwargs,
                log_formatter=log_formatter,
                exit_on_rate_limit=exit_on_rate_limit,
            )  # type: ignore # mypy can't infer that backoff_handler wraps _send

            return response
        except BaseBackoffException as e:
            self._logger.error(f"Retries exhausted with backoff exception.", exc_info=True)
            raise MessageRepresentationAirbyteTracedErrors(
                internal_message=f"Exhausted available request attempts. Exception: {e}",
                message=f"Exhausted available request attempts. Please see logs for more details. Exception: {e}",
                failure_type=e.failure_type or FailureType.system_error,
                exception=e,
                stream_descriptor=StreamDescriptor(name=self._name),
            )

    def _send(
        self,
        request: requests.PreparedRequest,
        request_kwargs: Mapping[str, Any],
        log_formatter: Optional[Callable[[requests.Response], Any]] = None,
        exit_on_rate_limit: Optional[bool] = False,
    ) -> requests.Response:
        if request not in self._request_attempt_count:
            self._request_attempt_count[request] = 1
        else:
            self._request_attempt_count[request] += 1
            if hasattr(self._session, "auth") and isinstance(self._session.auth, AuthBase):
                self._session.auth(request)

        self._logger.debug(
            "Making outbound API request",
            extra={"headers": request.headers, "url": request.url, "request_body": request.body},
        )

        response: Optional[requests.Response] = None
        exc: Optional[requests.RequestException] = None

        try:
            response = self._session.send(request, **request_kwargs)
        except requests.RequestException as e:
            exc = e

        error_resolution: ErrorResolution = self._error_handler.interpret_response(
            response if response is not None else exc
        )

        # Evaluation of response.text can be heavy, for example, if streaming a large response
        # Do it only in debug mode
        if self._logger.isEnabledFor(logging.DEBUG) and response is not None:
            if request_kwargs.get("stream"):
                self._logger.debug(
                    "Receiving response, but not logging it as the response is streamed",
                    extra={"headers": response.headers, "status": response.status_code},
                )
            else:
                self._logger.debug(
                    "Receiving response",
                    extra={
                        "headers": response.headers,
                        "status": response.status_code,
                        "body": response.text,
                    },
                )

        # Request/response logging for declarative cdk
        if (
            log_formatter is not None
            and response is not None
            and self._message_repository is not None
        ):
            formatter = log_formatter
            self._message_repository.log_message(
                Level.DEBUG,
                lambda: formatter(response),
            )

        self._handle_error_resolution(
            response=response,
            exc=exc,
            request=request,
            error_resolution=error_resolution,
            exit_on_rate_limit=exit_on_rate_limit,
        )

        return response  # type: ignore # will either return a valid response of type requests.Response or raise an exception

    def _get_response_body(self, response: requests.Response) -> Optional[JsonType]:
        """
        Extracts and returns the body of an HTTP response.

        This method attempts to parse the response body as JSON. If the response
        body is not valid JSON, it falls back to decoding the response content
        as a UTF-8 string. If both attempts fail, it returns None.

        Args:
            response (requests.Response): The HTTP response object.

        Returns:
            Optional[JsonType]: The parsed JSON object as a string, the decoded
            response content as a string, or None if both parsing attempts fail.
        """
        try:
            return str(response.json())
        except requests.exceptions.JSONDecodeError:
            try:
                return response.content.decode("utf-8")
            except Exception:
                return "The Content of the Response couldn't be decoded."

    def _evict_key(self, prepared_request: requests.PreparedRequest) -> None:
        """
        Addresses high memory consumption when enabling concurrency in https://github.com/airbytehq/oncall/issues/6821.

        The `_request_attempt_count` attribute keeps growing as multiple requests are made using the same `http_client`.
        To mitigate this issue, we evict keys for completed requests once we confirm that no further retries are needed.
        This helps manage memory usage more efficiently while maintaining the necessary logic for retry attempts.
        """
        if prepared_request in self._request_attempt_count:
            del self._request_attempt_count[prepared_request]

    def _handle_error_resolution(
        self,
        response: Optional[requests.Response],
        exc: Optional[requests.RequestException],
        request: requests.PreparedRequest,
        error_resolution: ErrorResolution,
        exit_on_rate_limit: Optional[bool] = False,
    ) -> None:
        if error_resolution.response_action not in self._ACTIONS_TO_RETRY_ON:
            self._evict_key(request)

        if error_resolution.response_action == ResponseAction.RESET_PAGINATION:
            raise PaginationResetRequiredException()

        # Emit stream status RUNNING with the reason RATE_LIMITED to log that the rate limit has been reached
        if error_resolution.response_action == ResponseAction.RATE_LIMITED:
            # TODO: Update to handle with message repository when concurrent message repository is ready
            reasons = [AirbyteStreamStatusReason(type=AirbyteStreamStatusReasonType.RATE_LIMITED)]
            message = orjson.dumps(
                AirbyteMessageSerializer.dump(
                    stream_status_as_airbyte_message(
                        StreamDescriptor(name=self._name), AirbyteStreamStatus.RUNNING, reasons
                    )
                )
            ).decode()

            # Simply printing the stream status is a temporary solution and can cause future issues. Currently, the _send method is
            # wrapped with backoff decorators, and we can only emit messages by iterating record_iterator in the abstract source at the
            # end of the retry decorator behavior. This approach does not allow us to emit messages in the queue before exiting the
            # backoff retry loop. Adding `\n` to the message and ignore 'end' ensure that few messages are printed at the same time.
            print(f"{message}\n", end="", flush=True)

        if error_resolution.response_action == ResponseAction.FAIL:
            if response is not None:
                filtered_response_message = filter_secrets(
                    f"Request (body): '{str(request.body)}'. Response (body): '{self._get_response_body(response)}'. Response (headers): '{response.headers}'."
                )
                error_message = f"'{request.method}' request to '{request.url}' failed with status code '{response.status_code}' and error message: '{self._error_message_parser.parse_response_error_message(response)}'. {filtered_response_message}"
            else:
                error_message = (
                    f"'{request.method}' request to '{request.url}' failed with exception: '{exc}'"
                )

            # ensure the exception message is emitted before raised
            self._logger.error(error_message)

            raise MessageRepresentationAirbyteTracedErrors(
                internal_message=error_message,
                message=error_resolution.error_message or error_message,
                failure_type=error_resolution.failure_type,
            )

        elif error_resolution.response_action == ResponseAction.IGNORE:
            if response is not None:
                log_message = f"Ignoring response for '{request.method}' request to '{request.url}' with response code '{response.status_code}'"
            else:
                log_message = f"Ignoring response for '{request.method}' request to '{request.url}' with error '{exc}'"

            self._logger.info(error_resolution.error_message or log_message)

        # TODO: Consider dynamic retry count depending on subsequent error codes
        elif (
            error_resolution.response_action == ResponseAction.RETRY
            or error_resolution.response_action == ResponseAction.RATE_LIMITED
        ):
            user_defined_backoff_time = None
            for backoff_strategy in self._backoff_strategies:
                backoff_time = backoff_strategy.backoff_time(
                    response_or_exception=response if response is not None else exc,
                    attempt_count=self._request_attempt_count[request],
                )
                if backoff_time:
                    user_defined_backoff_time = backoff_time
                    break
            error_message = (
                error_resolution.error_message
                or f"Request to {request.url} failed with failure type {error_resolution.failure_type}, response action {error_resolution.response_action}."
            )

            retry_endlessly = (
                error_resolution.response_action == ResponseAction.RATE_LIMITED
                and not exit_on_rate_limit
            )

            if user_defined_backoff_time:
                raise UserDefinedBackoffException(
                    backoff=user_defined_backoff_time,
                    request=request,
                    response=(response if response is not None else exc),
                    error_message=error_message,
                    failure_type=error_resolution.failure_type,
                )

            elif retry_endlessly:
                raise RateLimitBackoffException(
                    request=request,
                    response=(response if response is not None else exc),
                    error_message=error_message,
                    failure_type=error_resolution.failure_type,
                )

            raise DefaultBackoffException(
                request=request,
                response=(response if response is not None else exc),
                error_message=error_message,
                failure_type=error_resolution.failure_type,
            )

        elif response:
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                self._logger.error(response.text)
                raise e

    @property
    def name(self) -> str:
        return self._name

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
        exit_on_rate_limit: Optional[bool] = False,
    ) -> Tuple[requests.PreparedRequest, requests.Response]:
        """
        Prepares and sends request and return request and response objects.
        """

        request: requests.PreparedRequest = self._create_prepared_request(
            http_method=http_method,
            url=url,
            dedupe_query_params=dedupe_query_params,
            headers=headers,
            params=params,
            json=json,
            data=data,
        )

        env_settings = self._session.merge_environment_settings(
            url=request.url,
            proxies=request_kwargs.get("proxies", {}),
            stream=request_kwargs.get("stream"),
            verify=request_kwargs.get("verify"),
            cert=request_kwargs.get("cert"),
        )
        request_kwargs = {**request_kwargs, **env_settings}

        response: requests.Response = self._send_with_retry(
            request=request,
            request_kwargs=request_kwargs,
            log_formatter=log_formatter,
            exit_on_rate_limit=exit_on_rate_limit,
        )

        return request, response
