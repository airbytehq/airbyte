#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import requests
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.response import Response


class JsonDecoder(Decoder):
    def decode(self, response: requests.Response) -> Response:
        return Response(response.json())
