#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.types import Record


@dataclass
class PocketExtractor(RecordExtractor):
    """
    Record extractor that extracts record of the form:

    { "list": { "ID_1": record_1, "ID_2": record_2, ... } }

    Attributes:
        parameters (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
        decoder (Decoder): The decoder responsible to transfom the response in a Mapping
        field_path (str): The field defining record Mapping
    """

    parameters: InitVar[Mapping[str, Any]]
    field_path: str = "list"

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_body = response.json()
        if self.field_path not in response_body:
            return []
        elif type(response_body[self.field_path]) is list:
            return response_body[self.field_path]
        else:
            return [record for _, record in response_body[self.field_path].items()]
