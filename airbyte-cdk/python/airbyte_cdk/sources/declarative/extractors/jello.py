#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import List, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.types import Config, Record
from jello import lib as jello_lib


class JelloExtractor:
    """
    Record extractor that evaluates a Jello query to extract records from a decoded response.

    More information on Jello can be found at https://github.com/kellyjonbrazil/jello
    """

    default_transform = "_"

    def __init__(self, transform: Union[InterpolatedString, str], config: Config, decoder: Decoder = JsonDecoder()):
        """
        :param transform: The Jello query to evaluate on the decoded response
        :param config: The user-provided configuration as specified by the source's spec
        :param decoder: The decoder responsible to transfom the response in a Mapping
        """

        if isinstance(transform, str):
            transform = InterpolatedString(transform, default=self.default_transform)

        self._transform = transform
        self._decoder = decoder
        self._config = config

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_body = self._decoder.decode(response)
        script = self._transform.eval(self._config)
        return jello_lib.pyquery(response_body, script)
