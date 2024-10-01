#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Generator, Mapping
import requests

from airbyte_cdk.sources.declarative.decoders import Decoder


class PaginationDecoder:
    """
    Decoder to wrap other decoders when instantiating a DefaultPaginator in order to bypass decoding if the response is streamed.
    """
    def __init__(self, decoder: Decoder):
        self._decoder = decoder

    def is_stream_response(self) -> bool:
        return self._decoder.is_stream_response

    def decode(self, response: requests.Response) -> Generator[Mapping[str, Any], None, None]:
        if self.is_stream_response():
            return {}
        else:
            yield from self._decoder.decode(response)
