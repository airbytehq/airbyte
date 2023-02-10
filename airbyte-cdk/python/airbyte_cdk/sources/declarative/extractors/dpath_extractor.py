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


@dataclass
class DpathExtractor(RecordExtractor):
    """
    Record extractor that searches a decoded response over a path defined as an array of fields.

    If the field path points to an array, that array is returned.
    If the field path points to an object, that object is returned wrapped as an array.
    If the field path points to an empty object, an empty array is returned.
    If the field path points to a non-existing path, an empty array is returned.

    Examples of instantiating this transform:
    ```
      extractor:
        type: DpathExtractor
        field_path:
          - "root"
          - "data"
    ```

    ```
      extractor:
        type: DpathExtractor
        field_path:
          - "root"
          - "{{ parameters['field'] }}"
    ```

    ```
      extractor:
        type: DpathExtractor
        field_path: []
    ```

    Attributes:
        field_path (Union[InterpolatedString, str]): Path to the field that should be extracted
        config (Config): The user-provided configuration as specified by the source's spec
        decoder (Decoder): The decoder responsible to transfom the response in a Mapping
    """

    field_path: List[Union[InterpolatedString, str]]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    decoder: Decoder = JsonDecoder(parameters={})

    def __post_init__(self, parameters: Mapping[str, Any]):
        for path_index in range(len(self.field_path)):
            if isinstance(self.field_path[path_index], str):
                self.field_path[path_index] = InterpolatedString.create(self.field_path[path_index], parameters=parameters)

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_body = self.decoder.decode(response)
        if len(self.field_path) == 0:
            extracted = response_body
        else:
            path = [path.eval(self.config) for path in self.field_path]
            if "*" in path:
                extracted = dpath.util.values(response_body, path)
            else:
                extracted = dpath.util.get(response_body, path, default=[])
        if isinstance(extracted, list):
            return extracted
        elif extracted:
            return [extracted]
        else:
            return []
