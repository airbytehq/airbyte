#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Tuple

from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import Oauth2Authenticator
from typing import Any, List, Mapping, MutableMapping, Tuple

class Crm365Oauth2Authenticator(Oauth2Authenticator):

    def build_refresh_request_body(self) -> Mapping[str, Any]:
        """
        Returns the request body to set on the refresh request
        """
        payload: MutableMapping[str, Any] = {
            "grant_type": "client_credentials",
            "client_id": self.get_client_id(),
            "client_secret": self.get_client_secret(),
            "scope": self.get_scopes()
        }

        return payload