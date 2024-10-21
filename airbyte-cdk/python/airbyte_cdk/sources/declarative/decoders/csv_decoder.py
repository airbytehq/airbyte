#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import csv
import io
import logging
from dataclasses import InitVar, dataclass
from typing import Any, Generator, Mapping, MutableMapping

import requests

from airbyte_cdk.sources.declarative.decoders.decoder import Decoder

logger = logging.getLogger("airbyte")


@dataclass
class CsvDecoder(Decoder):
    """
    CsvDecoder is a decoder strategy that parses the CSV content of the response, and converts it to a stream of dicts.
    """

    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.delimiter = parameters.get("delimiter", ",")

    def is_stream_response(self) -> bool:
        return False

    def decode(self, response: requests.Response) -> Generator[MutableMapping[str, Any], None, None]:
        try:
            csv_content = io.StringIO(response.text)
            reader = csv.reader(csv_content, delimiter=self.delimiter)
            header = next(reader)

            for row in reader:
                record = {}
                for i, value in enumerate(row):
                    if i < len(header):
                        record[header[i]] = value
                yield record

        except Exception as exc:
            logger.warning(f"Response cannot be parsed from CSV: {response.status_code=}, {response.text=}, {exc=}")
            yield {}
