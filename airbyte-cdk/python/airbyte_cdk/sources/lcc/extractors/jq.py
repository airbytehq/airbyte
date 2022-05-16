#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import List

import pyjq
import requests
from airbyte_cdk.sources.lcc.extractors.http_extractor import HttpExtractor
from airbyte_cdk.sources.lcc.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.lcc.types import Record


class JqExtractor(HttpExtractor):
    default_transform = "."

    def __init__(self, transform: str, config, kwargs=None):
        if kwargs is None:
            kwargs = dict()
        self._vars = vars
        self._interpolator = JinjaInterpolation()
        self._transform = transform
        self._config = config
        self._kwargs = kwargs

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_body = response.json()
        script = self._interpolator.eval(self._transform, self._config, default=self.default_transform, **{"kwargs": self._kwargs})
        return pyjq.all(script, response_body)
