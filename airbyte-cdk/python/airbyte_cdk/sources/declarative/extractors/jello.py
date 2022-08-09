#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import InitVar, dataclass
from typing import Any, List, Mapping, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config, Record
from dataclasses_jsonschema import JsonSchemaMixin
from jello import lib as jello_lib


@dataclass
class JelloExtractor(JsonSchemaMixin):
    """
    Record extractor that evaluates a Jello query to extract records from a decoded response.

    More information on Jello can be found at https://github.com/kellyjonbrazil/jello

    Attributes:
        transform (Union[InterpolatedString, str]): The Jello query to evaluate on the decoded response
        config (Config): The user-provided configuration as specified by the source's spec
        decoder (Decoder): The decoder responsible to transfom the response in a Mapping
    """

    default_transform = "_"
    transform: Union[InterpolatedString, str]
    config: Config
    options: InitVar[Mapping[str, Any]]
    decoder: Decoder = JsonDecoder(options={})

    def __post_init__(self, options: Mapping[str, Any]):
        if isinstance(self.transform, str):
            self.transform = InterpolatedString(string=self.transform, default=self.default_transform, options=options or {})

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_body = self.decoder.decode(response)
        script = self.transform.eval(self.config)
        return jello_lib.pyquery(response_body, script)
