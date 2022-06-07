#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Union

from airbyte_cdk.sources.declarative.extractors.http_extractor import HttpExtractor
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.response import Response
from airbyte_cdk.sources.declarative.types import Record
from jello import lib as jello_lib


class JqExtractor(HttpExtractor):
    default_transform = "."

    def __init__(self, transform: str, config, kwargs=None):
        if kwargs is None:
            kwargs = dict()
        self._interpolator = JinjaInterpolation()
        self._transform = transform
        self._config = config
        self._kwargs = kwargs

    def extract_records(self, response: Response) -> Union[List[Record], Mapping[str, Any]]:
        script = self._interpolator.eval(self._transform, self._config, default=self.default_transform, **{"kwargs": self._kwargs})
        return jello_lib.pyquery(response.body, script)
