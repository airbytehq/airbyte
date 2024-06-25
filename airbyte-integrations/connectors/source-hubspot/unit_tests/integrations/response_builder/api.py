# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from typing import List

from airbyte_cdk.test.mock_http import HttpResponse

from . import AbstractResponseBuilder


class ScopesResponseBuilder(AbstractResponseBuilder):
    def __init__(self, scopes: List[str]):
        self._scopes = scopes

    def build(self):
        body = json.dumps({"scopes": self._scopes})
        return HttpResponse(body=body, status_code=200)
