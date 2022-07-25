#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.types import Record
from jello import lib as jello_lib


class JelloExtractor:
    default_transform = "."

    def __init__(self, transform: str, decoder: Optional[Decoder] = None, config=None, kwargs=None):
        self._interpolator = JinjaInterpolation()
        self._transform = transform
        self._decoder = decoder or JsonDecoder()
        self._config = config
        self._kwargs = kwargs or dict()

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_body = self._decoder.decode(response)
        script = self._interpolator.eval(self._transform, self._config, default=self.default_transform, **{"kwargs": self._kwargs})
        return jello_lib.pyquery(response_body, script)
