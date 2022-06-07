#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

import pyjq
import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.extractors.http_extractor import HttpExtractor
from airbyte_cdk.sources.declarative.interpolation.interpolated_boolean import InterpolatedBoolean
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.types import Record


class JqExtractor(HttpExtractor):
    default_transform = "."

    def __init__(self, transform: str, decoder: Decoder, config, record_filter: str = None, kwargs=None):
        if kwargs is None:
            kwargs = dict()
        self._interpolator = JinjaInterpolation()
        self._transform = transform
        self._config = config
        self._kwargs = kwargs
        self._decoder = decoder

        if record_filter:
            self._filter_interpolator = InterpolatedBoolean(record_filter)
        else:
            self._filter_interpolator = None

    def extract_records(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> List[Record]:
        response_body = self._decoder.decode(response)
        script = self._interpolator.eval(self._transform, self._config, default=self.default_transform, **{"kwargs": self._kwargs})
        all_records = pyjq.all(script, response_body)

        kwargs = {"stream_state": stream_state, "stream_slice": stream_slice, "next_page_token": next_page_token}
        if self._filter_interpolator:
            return [record for record in all_records if self._filter_interpolator.eval(self._config, record=record, **kwargs)]
        return all_records
