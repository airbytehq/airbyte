#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import dataclass
from typing import Any, Generator, MutableMapping

import requests
from airbyte_cdk.sources.declarative.decoders import Decoder

logger = logging.getLogger("airbyte")


@dataclass
class PaginationDecoderDecorator(Decoder):
    """
    Decoder to wrap other decoders when instantiating a DefaultPaginator in order to bypass decoding if the response is streamed.
    """

    def __init__(self, decoder: Decoder):
        self._decoder = decoder

    @property
    def decoder(self) -> Decoder:
        return self._decoder

    def is_stream_response(self) -> bool:
        return self._decoder.is_stream_response()

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        if self._decoder.is_stream_response():
            logger.warning("Response is streamed and therefore will not be decoded for pagination.")
            yield {}
        else:
            yield from self._decoder.decode(response)
