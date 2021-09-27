#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping

from base_python.cdk.streams.auth.core import HttpAuthenticator


class JWTAuthenticator(HttpAuthenticator):
    def get_auth_header(self) -> Mapping[str, Any]:
        # TODO
        raise NotImplementedError
