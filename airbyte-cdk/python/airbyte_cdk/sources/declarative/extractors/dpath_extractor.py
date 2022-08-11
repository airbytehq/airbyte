#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
class DpathExtractor(RecordExtractor, JsonSchemaMixin):
    """
    Record extractor that searches a decoded response over a path defined as an array of fields.

    If the field pointer points to an array, that array is returned.
    If the field pointer points to an object, that object is returned wrapped as an array.
    If the field pointer points to an empty object, an empty array is returned.
    If the field pointer points to a non-existing path, an empty array is returned.

    Examples of instantiating this transform:
    ```
      extractor:
        type: DpathExtractor
        field_pointer:
          - "root"
          - "data"
    ```

    ```
      extractor:
        type: DpathExtractor
        field_pointer:
          - "root"
          - "{{ options['field'] }}"
    ```

    ```
      extractor:
        type: DpathExtractor
        field_pointer: []
    ```

    Attributes:
        transform (Union[InterpolatedString, str]): Pointer to the field that should be extracted
        config (Config): The user-provided configuration as specified by the source's spec
        decoder (Decoder): The decoder responsible to transfom the response in a Mapping
    """

    field_pointer: List[Union[InterpolatedString, str]]
    config: Config
    options: InitVar[Mapping[str, Any]]
    decoder: Decoder = JsonDecoder(options={})

    def __post_init__(self, options: Mapping[str, Any]):
        for pointer_index in range(len(self.field_pointer)):
            if isinstance(self.field_pointer[pointer_index], str):
                self.field_pointer[pointer_index] = InterpolatedString.create(self.field_pointer[pointer_index], options=options)

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_body = self.decoder.decode(response)
        if len(self.field_pointer) == 0:
            extracted = response_body
        else:
            pointer = [pointer.eval(self.config) for pointer in self.field_pointer]
            extracted = dpath.util.get(response_body, pointer, default=[])
        if isinstance(extracted, list):
            return extracted
        elif extracted:
            return [extracted]
        else:
            return []
