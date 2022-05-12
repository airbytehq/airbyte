#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import List

import pyjq
import requests
from airbyte_cdk.sources.cac.extractors.extractor import Extractor
from airbyte_cdk.sources.cac.interpolation.eval import JinjaInterpolation
from airbyte_cdk.sources.cac.types import Record


class JqExtractor(Extractor):
    def __init__(self, transform, vars=None, config=None):
        if vars is None:
            vars = dict()
        if config is None:
            config = dict()
        self._vars = vars
        self._config = config
        self._interpolator = JinjaInterpolation()
        self._transform = transform

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_body = response.json()
        # FIXME: need to ensure I'm passing the vars and the parent vars...
        script = self._interpolator.eval(self._transform, self._vars, self._config)
        return pyjq.all(script, response_body)
