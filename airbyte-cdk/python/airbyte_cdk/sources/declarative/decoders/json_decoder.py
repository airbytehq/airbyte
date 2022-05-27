#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Mapping, Union

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.response import Response


class JsonDecoder(Decoder):
    def decode(self, response: Union[Mapping[str, str], requests.Response]) -> Response:
        if isinstance(response, requests.Response):
            return Response(response.json())
        else:
            return Response(response)
