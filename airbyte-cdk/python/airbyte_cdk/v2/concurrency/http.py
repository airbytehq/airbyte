import dataclasses
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Any, Union, AsyncIterable, TypeVar, Generic, Optional, Tuple

import aiohttp

from airbyte_cdk.v2.concurrency.async_requesters import AsyncRequester, Client, RequestType
from airbyte_cdk.v2.concurrency.partition_descriptors import PartitionDescriptor


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
    body_json: Mapping[str, Any] = None
    paginator: Optional[
        "Paginator"] = None  # FIXME: I liked that this was a dataclass. adding the paginator here isn't great + it creates a circular dependency


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


ResponseType = TypeVar('ResponseType')


class Paginator(ABC, Generic[ResponseType]):
    @abstractmethod
    def get_next_page_info(self, response: ResponseType, partition: PartitionDescriptor) -> Optional[HttpRequestDescriptor]:
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
        return None


class RequestGenerator:
    async def next_request(self, partition_descriptor: PartitionDescriptor, response: Optional[aiohttp.ClientResponse]) -> Optional[
        HttpRequestDescriptor]:
        """
        :param partition_descriptor:
        :param response: last response. Used to generate the next request if needed
        :return:
        """
        pass


class AiohttpClient(Client[HttpRequestDescriptor, aiohttp.ClientResponse]):
    def __init__(self):
        self._client: aiohttp.ClientSession = None

    async def get_client(self):
        if not self._client:
            self._client = aiohttp.ClientSession()
            await self._client.__aenter__()

        return self._client

    async def request(self, request: HttpRequestDescriptor) -> aiohttp.ClientResponse:
        args = {
            'headers': request.headers,
            'allow_redirects': request.follow_redirects,
            'cookies': request.cookies
        }
        if isinstance(request, GetRequest):
            get_descriptor: GetRequest = request
            args['params'] = get_descriptor.request_parameters
        elif isinstance(request, PostRequest):
            post_descriptor: PostRequest = request
            args['json'] = post_descriptor.body_json
            args['data'] = post_descriptor.body_data
        return (await self.get_client()).request(request.method, request.base_url + request.path,  **args)


class AiohttpRequester(AsyncRequester):
    def __init__(self, client: AiohttpClient, request_generator: RequestGenerator, error_handler: ErrorHandler = None):
        self._request_generator = request_generator
        # FIXME: can we initialize the client in __init__?
        self._client = client
        # TODO this should be a list of error handlers
        self.error_handler = error_handler or DefaultExponentialBackoffHandler()

    async def request(self, partition_descriptor: PartitionDescriptor) -> AsyncIterable[aiohttp.ClientResponse]:
        pagination_complete = False
        last_response = None
        while not pagination_complete:
            request = await self._request_generator.next_request(partition_descriptor, last_response)
            async with (await self._client.request(request)) as last_response:
                try:
                    self.error_handler.observe_response(last_response)
                except Retry as e:
                    # TODO implement retry logic
                    raise Exception(f"We should be retrying here!! {e}. Response: {last_response} ")
                else:
                    print(f"response: {last_response}")
                    yield last_response
                    request = await self._request_generator.next_request(partition_descriptor, last_response)
                    pagination_complete = request is None

    @staticmethod
    def _get_request_args(request_descriptor: HttpRequestDescriptor) -> Tuple[str, str, Mapping[str, Any]]:
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
