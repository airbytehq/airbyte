#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.types import Record


@dataclass
class PocketExtractor(RecordExtractor):
    """
    Record extractor that extracts record of the form:

    { "list": { "ID_1": record_1, "ID_2": record_2, ... } }

    Attributes:
        options (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
        decoder (Decoder): The decoder responsible to transfom the response in a Mapping
        field_pointer (str): The field defining record Mapping
    """

    options: InitVar[Mapping[str, Any]]
    decoder: Decoder = JsonDecoder(options={})
    field_pointer: str = "list"

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_body = self.decoder.decode(response)
        if self.field_pointer not in response_body:
            return []
        elif type(response_body[self.field_pointer]) is list:
            return response_body[self.field_pointer]
        else:
            return [record for _, record in response_body[self.field_pointer].items()]
