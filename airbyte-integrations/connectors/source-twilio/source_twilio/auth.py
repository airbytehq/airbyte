#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
from typing import Tuple

from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator


class HttpBasicAuthenticator(TokenAuthenticator):
    def __init__(self, auth: Tuple[str, str], auth_method: str = "Basic", **kwargs):
        auth_string = f"{auth[0]}:{auth[1]}".encode("utf8")
        b64_encoded = base64.b64encode(auth_string).decode("utf8")
        super().__init__(token=b64_encoded, auth_method=auth_method, **kwargs)
