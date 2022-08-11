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
    Record extractor that evaluates a Jello query to extract records from a decoded response.

    More information on Jello can be found at https://github.com/kellyjonbrazil/jello

    Attributes:
        transform (Union[InterpolatedString, str]): The Jello query to evaluate on the decoded response
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
        return dpath.util.get(response_body, [pointer.eval(self.config) for pointer in self.field_pointer], default=[])
