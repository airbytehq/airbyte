import dataclasses
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Any, Union, AsyncIterable, TypeVar, Generic, Optional, Tuple

import aiohttp

from airbyte_cdk.v2.concurrency import PartitionDescriptor, AsyncRequester


class ResponseParser:
    pass


@dataclass
class HttpRequestDescriptor:
    base_url: str
    path: str
    method: str
    headers: Mapping[str, Any] = field(default_factory=dict)
    cookies: Mapping[str, Any] = field(default_factory=dict)
    follow_redirects: bool = True


@dataclass
class GetRequest(HttpRequestDescriptor):
    request_parameters: Mapping[str, Any] = field(default_factory=dict)
    method: str = field(default="GET", init=False)


@dataclass
class PostRequest(HttpRequestDescriptor):
    body_data: Union[str, Mapping[str, Any]] = None
    body_json: Mapping[str, Any] = None
    method: str = field(default="POST", init=False)

    def __post_init__(self):
        num_input_body_params = sum(x is not None for x in [self.body_json, self.body_data])
        if num_input_body_params != 1:
            raise ValueError("Exactly one of of body_text, body_json, or body_urlencoded_params must be set")


@dataclass
class HttpPartitionDescriptor(PartitionDescriptor):
    request_descriptor: HttpRequestDescriptor


ResponseType = TypeVar('ResponseType')


class Paginator(ABC, Generic[ResponseType]):
    @abstractmethod
    def get_next_page_info(self, response: ResponseType) -> HttpRequestDescriptor:
        """
        Given the response representing the previous page of data return an HttpRequestDescriptor containing any info for the next page
        """


class RequestException(Exception):
    pass


class Ignore(RequestException):
    def __init__(self, reason: str):
        self.reason = reason


class Retry(RequestException):
    def __init__(self, reason: str, retry_after_seconds: int):
        self.reason = reason
        retry_after_seconds = retry_after_seconds


class GracefullyEndSync(RequestException):
    def __init__(self, reason: str):
        reason = reason


class FailSync(RequestException):
    def __init__(self, reason: str, exception: BaseException, **kwargs):
        reason = reason
        exception = exception


class ErrorHandler(ABC, Generic[ResponseType]):
    @abstractmethod
    def observe_response(self, response: ResponseType) -> Optional[RequestException]:
        """"""


class DefaultExponentialBackoffHandler(ErrorHandler[aiohttp.ClientResponse]):
    def __init__(self, factor: int = 3):
        self.factor = factor
        self.request_to_attempt_number = defaultdict(int)

    # TODO pass attempt number
    def observe_response(self, response: aiohttp.ClientResponse) -> Optional[RequestException]:
        if response.status == 429 or response.status >= 500:
            wait_time = self.request_to_attempt_number[response.request_info] ** self.factor
            self.request_to_attempt_number[response.request_info] = self.request_to_attempt_number[response.request_info] + 1
            raise Retry(f"retrying due to response status code: {response.status}", wait_time)


class AiohttpRequester(AsyncRequester[HttpPartitionDescriptor]):
    def __init__(self, paginator: Paginator[aiohttp.ClientResponse], error_handler: ErrorHandler = None):
        self._client = None
        self.paginator = paginator
        # TODO this should be a list of error handlers
        self.error_handler = error_handler or DefaultExponentialBackoffHandler()

    async def get_client(self) -> aiohttp.ClientSession:
        if not self._client:
            self._client = aiohttp.ClientSession()
            await self._client.__aenter__()
        return self._client

    async def request(self, partition_descriptor: HttpPartitionDescriptor) -> AsyncIterable[aiohttp.ClientResponse]:
        method, url, request_description = self._get_request_args(partition_descriptor)
        # async with self.client() as client:
        async with (await self.get_client()).request(method, url, **request_description) as response:
            try:
                self.error_handler.observe_response(response)
            except Retry as e:
                # TODO implement retry logic
                raise Exception(f"We should be retrying here!! {e}. Response: {response} ")
            else:
                yield response

    @staticmethod
    def _get_request_args(partition_descriptor: HttpPartitionDescriptor) -> Tuple[str, str, Mapping[str, Any]]:
        request_descriptor = partition_descriptor.request_descriptor
        args = {
            'headers': request_descriptor.headers,
            'allow_redirects': request_descriptor.follow_redirects,
            'cookies': request_descriptor.cookies
        }

        if isinstance(request_descriptor, GetRequest):
            get_descriptor: GetRequest = request_descriptor
            args['params'] = get_descriptor.request_parameters
        elif isinstance(request_descriptor, PostRequest):
            post_descriptor: PostRequest = request_descriptor
            args['json'] = post_descriptor.body_json
            args['data'] = post_descriptor.body_data
        return request_descriptor.method, request_descriptor.base_url + request_descriptor.path, args
