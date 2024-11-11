import json

from airbyte_cdk.sources.declarative.decoders import Decoder

from dataclasses import dataclass
from typing import Any, Generator, MutableMapping

import requests

from gzip import decompress


@dataclass
class GzipDecoder(Decoder):

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        raw_string = decompress(response.content).decode("utf")
        yield from json.loads(raw_string)
