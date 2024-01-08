#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
)
from yarl import URL

import aiohttp
import aiohttp_client_cache
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.async_cdk.streams.async_call_rate import (
    AsyncCachedLimiterSession,
    AsyncLimiterSession,
)
from airbyte_cdk.sources.async_cdk.streams.core_async import AsyncStream
from airbyte_cdk.sources.async_cdk.streams.http.availability_strategy_async import (
    AsyncHttpAvailabilityStrategy,
)
from airbyte_cdk.sources.async_cdk.streams.http.exceptions_async import (
    DefaultBackoffException,
    RequestBodyException,
    UserDefinedBackoffException,
)
from airbyte_cdk.sources.http_config import MAX_CONNECTION_POOL_SIZE
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http.auth import NoAuth
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.streams.http.http_base import BaseHttpStream
from airbyte_cdk.sources.streams.http.utils import HttpError
from airbyte_cdk.utils.constants import ENV_REQUEST_CACHE_PATH

from .rate_limiting_async import default_backoff_handler, user_defined_backoff_handler

# list of all possible HTTP methods which can be used for sending of request bodies
BODY_REQUEST_METHODS = ("GET", "POST", "PUT", "PATCH")
RecordsGeneratorFunction = Callable[
    [
        aiohttp.ClientRequest,
        aiohttp.ClientResponse,
        Mapping[str, Any],
        Optional[Mapping[str, Any]],
    ],
    AsyncGenerator[StreamData, None],
]


class AsyncHttpStream(BaseHttpStream, AsyncStream, ABC):
    """
    Base abstract class for an Airbyte Stream using the HTTP protocol with asyncio.

    Basic building block for users building an Airbyte source for an async HTTP API.
    """

    def __init__(
        self, authenticator: Optional[Union[HttpAuthenticator, NoAuth]] = NoAuth()
    ):
        # TODO: wire in rate limiting via ApiBudget
        self._api_budget = None
        self._session: Optional[aiohttp.ClientSession] = None
        # TODO: HttpStream handles other authentication codepaths, which may need to be added later
        self._authenticator = authenticator

    @property
    def authenticator(self) -> Optional[Union[HttpAuthenticator, NoAuth]]:
        # TODO: this behaves differently than http.py, which would return None if self._authenticator is an HttpAuthenticator.
        #  But, it looks like this property is only used here in http_async.py and Salesforce's streams.py.
        #  It doesn't appear to be causing any problems with Salesforce.
        return self._authenticator

    @property
    def availability_strategy(self) -> Optional[AsyncHttpAvailabilityStrategy]:
        return AsyncHttpAvailabilityStrategy()

    def request_session(self) -> aiohttp.ClientSession:
        """
        Session factory based on use_cache property and call rate limits (api_budget parameter)
        :return: instance of request-based session
        """
        connector = aiohttp.TCPConnector(
            limit_per_host=MAX_CONNECTION_POOL_SIZE,
            limit=MAX_CONNECTION_POOL_SIZE,
        )
        kwargs = {}

        if self._authenticator:
            kwargs["headers"] = self._authenticator.get_auth_header()

        if self.use_cache:
            cache_dir = os.getenv(ENV_REQUEST_CACHE_PATH)
            # Use in-memory cache if cache_dir is not set
            # This is a non-obvious interface, but it ensures we don't write sql files when running unit tests
            if cache_dir:
                sqlite_path = str(Path(cache_dir) / self.cache_filename)
            else:
                sqlite_path = "file::memory:?cache=shared"
            cache = aiohttp_client_cache.SQLiteBackend(
                cache_name=sqlite_path,
                allowed_methods=(
                    "get",
                    "post",
                    "put",
                    "patch",
                    "options",
                    "delete",
                    "list",
                ),
            )
            return AsyncCachedLimiterSession(
                cache=cache, connector=connector, api_budget=self._api_budget
            )
        else:
            return AsyncLimiterSession(
                connector=connector, api_budget=self._api_budget, **kwargs
            )

    async def clear_cache(self) -> None:
        """
        Clear cached requests for current session, can be called any time
        """
        if isinstance(self._session, aiohttp_client_cache.CachedSession):
            await self._session.cache.clear()

    @abstractmethod
    async def next_page_token(
        self, response: aiohttp.ClientResponse
    ) -> Optional[Mapping[str, Any]]:
        """
        Override this method to define a pagination strategy.

        The value returned from this method is passed to most other methods in this class. Use it to form a request e.g: set headers or query params.

        :return: The token for the next page from the input response object. Returning None means there are no more pages to read in this response.
        """

    @abstractmethod
    async def parse_response(
        self,
        response: aiohttp.ClientResponse,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> AsyncGenerator[Mapping[str, Any], None]:
        """
        Parses the raw response object into a list of records.
        By default, this returns an iterable containing the input. Override to parse differently.
        :param response:
        :param stream_state:
        :param stream_slice:
        :param next_page_token:
        :return: An iterable containing the parsed response
        """
        ...

    # TODO move all the retry logic to a functor/decorator which is input as an init parameter
    def should_retry(self, response: aiohttp.ClientResponse) -> bool:
        """
        Override to set different conditions for backoff based on the response from the server.

        By default, back off on the following HTTP response statuses:
         - 429 (Too Many Requests) indicating rate limiting
         - 500s to handle transient server errors

        Unexpected but transient exceptions (connection timeout, DNS resolution failed, etc..) are retried by default.
        """
        return response.status == 429 or 500 <= response.status < 600

    def backoff_time(self, response: aiohttp.ClientResponse) -> Optional[float]:
        """
        Override this method to dynamically determine backoff time e.g: by reading the X-Retry-After header.

        This method is called only if should_backoff() returns True for the input request.

        :param response:
        :return how long to backoff in seconds. The return value may be a floating point number for subsecond precision. Returning None defers backoff
        to the default backoff behavior (e.g using an exponential algorithm).
        """
        return None

    def error_message(self, response: aiohttp.ClientResponse) -> str:
        """
        Override this method to specify a custom error message which can incorporate the HTTP response received

        :param response: The incoming HTTP response from the partner API
        :return:
        """
        return ""

    def _create_prepared_request(
        self,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Mapping[str, str]] = None,
        json: Optional[Mapping[str, Any]] = None,
        data: Optional[Union[str, Mapping[str, Any]]] = None,
    ) -> aiohttp.ClientRequest:
        return self._create_aiohttp_client_request(path, headers, params, json, data)

    def _create_aiohttp_client_request(
        self,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Mapping[str, str]] = None,
        json_data: Optional[Mapping[str, Any]] = None,
        data: Optional[Union[str, Mapping[str, Any]]] = None,
    ) -> aiohttp.ClientRequest:
        str_url = self._join_url(self.url_base, path)
        # str_url = "http://localhost:8000"  # TODO
        url = URL(str_url)
        if self.must_deduplicate_query_params():
            query_params = self.deduplicate_query_params(str_url, params)
        else:
            query_params = params or {}
        if self.http_method.upper() in BODY_REQUEST_METHODS:
            if json_data and data:
                raise RequestBodyException(
                    "At the same time only one of the 'request_body_data' and 'request_body_json' functions can return data"
                )
            elif json_data:
                headers = headers or {}
                headers.update({"Content-Type": "application/json"})
                data = json.dumps(json_data)

        client_request = aiohttp.ClientRequest(
            self.http_method, url, headers=headers, params=query_params, data=data
        )

        return client_request

    async def _send(
        self, request: aiohttp.ClientRequest, request_kwargs: Mapping[str, Any]
    ) -> aiohttp.ClientResponse:
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
            "Making outbound API request",
            extra={
                "headers": request.headers,
                "url": request.url,
                "request_body": request.body,
            },
        )
        if self._session is None:
            raise AssertionError(
                "The session was not set before attempting to make a request. This is unexpected. Please contact Support."
            )

        response = await self._session.request(
            request.method,
            request.url,
            headers=request.headers,
            auth=request.auth,
            **request_kwargs,
        )

        # Evaluation of response.text can be heavy, for example, if streaming a large response
        # Do it only in debug mode
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                "Receiving response",
                extra={
                    "headers": response.headers,
                    "status": response.status,
                    "body": response.text,
                },
            )
        try:
            return await self.handle_response_with_error(response)
        except HttpError as exc:
            if self.should_retry(response):
                custom_backoff_time = self.backoff_time(response)
                error_message = self.error_message(response)
                if custom_backoff_time:
                    raise UserDefinedBackoffException(
                        backoff=custom_backoff_time,
                        error=exc,
                        error_message=error_message,
                    )
                else:
                    raise DefaultBackoffException(
                        error=exc, error_message=error_message
                    )
            elif self.raise_on_http_errors:
                # Raise any HTTP exceptions that happened in case there were unexpected ones
                raise exc
            return response

    async def ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = self.request_session()
        return self._session

    async def _send_request(
        self, request: aiohttp.ClientRequest, request_kwargs: Mapping[str, Any]
    ) -> aiohttp.ClientResponse:
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
        max_time = self.max_time
        """
        According to backoff max_time docstring:
            max_time: The maximum total amount of time to try for before
                giving up. Once expired, the exception will be allowed to
                escape. If a callable is passed, it will be
                evaluated at runtime and its return value used.
        """
        if max_tries is not None:
            max_tries = max(0, max_tries) + 1

        user_backoff_handler = user_defined_backoff_handler(
            max_tries=max_tries, max_time=max_time
        )(self._send)
        backoff_handler = default_backoff_handler(
            max_tries=max_tries, max_time=max_time, factor=self.retry_factor
        )
        return await backoff_handler(user_backoff_handler)(request, request_kwargs)

    @classmethod
    def parse_response_error_message(cls, response: requests.Response) -> Optional[str]:
        raise NotImplementedError(
            "Async streams should use HttpError.parse_error_message"
        )

    async def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> AsyncGenerator[StreamData, None]:
        async def _records_generator_fn(
            req, res, state, _slice
        ) -> AsyncGenerator[StreamData, None]:
            async for record in self.parse_response(
                res, stream_slice=_slice, stream_state=state
            ):
                yield record

        async for record in self._read_pages(
            _records_generator_fn, stream_slice, stream_state
        ):
            yield record

    async def _read_pages(
        self,
        records_generator_fn: RecordsGeneratorFunction,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> AsyncGenerator[StreamData, None]:
        stream_state = stream_state or {}
        pagination_complete = False
        next_page_token = None
        while not pagination_complete:

            async def f() -> Tuple[
                aiohttp.ClientRequest,
                aiohttp.ClientResponse,
                Optional[Mapping[str, Any]],
            ]:
                nonlocal next_page_token
                request, response = await self._fetch_next_page(
                    stream_slice, stream_state, next_page_token
                )
                next_page_token = await self.next_page_token(response)
                return request, response, next_page_token

            request, response, next_page_token = await f()

            async for record in records_generator_fn(
                request, response, stream_state, stream_slice
            ):
                yield record

            if not next_page_token:
                pagination_complete = True

    async def _fetch_next_page(
        self,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Tuple[aiohttp.ClientRequest, aiohttp.ClientResponse]:
        request_headers = self.request_headers(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )
        request = self._create_prepared_request(
            path=self.path(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
            ),
            headers=dict(
                request_headers,
                **self.authenticator.get_auth_header() if self.authenticator else {},
            ),
            params=self.request_params(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
            ),
            json=self.request_body_json(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
            ),
            data=self.request_body_data(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
            ),
        )
        request_kwargs = self.request_kwargs(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

        response = await self._send_request(request, request_kwargs)
        return request, response

    async def handle_response_with_error(
        self, response: aiohttp.ClientResponse
    ) -> aiohttp.ClientResponse:
        """
        If the response has a non-ok status code, raise an exception, otherwise return the response.

        When raising an exception, attach response json data to exception object.
        """
        if response.ok:
            return response

        exc = HttpError(
            aiohttp_error=aiohttp.ClientResponseError(
                response.request_info,
                response.history,
                status=response.status,
                message=response.reason or "",
                headers=response.headers,
            ),
        )
        await exc.set_response_data(response)
        text = await response.text()
        self.logger.error(text)
        raise exc


class AsyncHttpSubStream(AsyncHttpStream, ABC):
    def __init__(self, parent: AsyncHttpStream, **kwargs: Any):
        """
        :param parent: should be the instance of HttpStream class
        """
        super().__init__(**kwargs)
        self.parent = parent

    async def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> AsyncGenerator[Optional[Mapping[str, Any]], None]:
        await self.parent.ensure_session()
        # iterate over all parent stream_slices
        async for stream_slice in self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh,
            cursor_field=cursor_field,
            stream_state=stream_state,
        ):
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh,
                cursor_field=cursor_field,
                stream_slice=stream_slice,
                stream_state=stream_state,
            )

            # iterate over all parent records with current stream_slice
            async for record in parent_records:
                yield {"parent": record}
