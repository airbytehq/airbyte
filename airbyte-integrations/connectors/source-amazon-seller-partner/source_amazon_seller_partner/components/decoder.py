#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import csv
import gzip
import logging
from dataclasses import InitVar, dataclass
from io import StringIO
from typing import Any, Generator, Mapping, MutableMapping

import orjson
import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder

logger = logging.getLogger("airbyte")


@dataclass
class GzipCsvDecoder(Decoder):
    """
    Decoder strategy that returns the json-encoded content of a response, if any.
    """

    parameters: InitVar[Mapping[str, Any]]

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        try:
            document = gzip.decompress(response.content).decode("iso-8859-1")
        except gzip.BadGzipFile:
            document = response.content.decode("iso-8859-1")

        yield from csv.DictReader(StringIO(document), delimiter="\t")
