from typing import Optional

import aiohttp

from airbyte_cdk.v2.concurrency.http import Paginator, ResponseType, HttpRequestDescriptor, GetRequest
from airbyte_cdk.v2.concurrency.partition_descriptors import PartitionDescriptor


class HttpStreamPaginator(Paginator[aiohttp.ClientResponse]):

    def __init__(self, stream):
        self._stream = stream # type: HttpStream - there's a circular dependency here

    def get_next_page_info(self, response: ResponseType, partition: PartitionDescriptor) -> Optional[HttpRequestDescriptor]:
        """
        Given the response representing the previous page of data return an HttpRequestDescriptor containing any info for the next page
        """
        next_page_token = self._stream.next_page_token(response)
        if next_page_token:
            if self._stream.http_method == "GET":
                stream_slice = partition.metadata
                request = GetRequest(
                    base_url=self._stream.url_base,
                    path=self._stream.path(stream_state={}, stream_slice=stream_slice, next_page_token=next_page_token),
                    headers={**self._stream.request_headers(stream_state={}, stream_slice=stream_slice, next_page_token=next_page_token), **self._stream.authenticator.get_auth_header()},
                    request_parameters=self._stream.request_params(stream_state={}, stream_slice=stream_slice, next_page_token=next_page_token),
                    body_json=self._stream.request_body_json(stream_state={}, stream_slice=stream_slice, next_page_token=next_page_token),
                    paginator=self
                )
                return request
            else:
                raise ValueError(f"Unsupported http method: {self._stream.http_method}")

        else:
            return None
