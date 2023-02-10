#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Union

import dpath.util
import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config, Record
from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class DpathStringExtractor(RecordExtractor, JsonSchemaMixin):
    """
    Makes it easy to extract records from nested and complex structures (nested lists, dicts, mixed structures) by specifying dpath string.
    Example: For the following structure `S` we want to extract and combine all the "expected_records" list values all together in one list.
        >>> import dpath.util
        >>> S = {
        ...     "key": {
        ...         "subkey": [
        ...             {"expected_records": [ {"id": 1}, {"id": 2}, {"id": 3} ]},
        ...             {"expected_records": [ {"id": 4} ]}
        ...         ]
        ...     }
        ... }
        >>> dpath.util.values(S, "/key/subkey/*/expected_records/*")  # The result: [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}]
    # Now we are able to specify the `field_path` as a dpath interpolated string "/key/subkey/*/expected_records/*":
    record_selector:
        ...
        extractor:
            ...
            field_path: "/key/subkey/*/expected_records/*"
            class_name: "source_monday.DpathStringExtractor"
    """

    field_path: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    decoder: Decoder = JsonDecoder(parameters={})

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.field_path = InterpolatedString.create(self.field_path, parameters=parameters)
        self.field_path = self.field_path.eval(self.config)

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_body = self.decoder.decode(response)
        return dpath.util.values(response_body, self.field_path)
