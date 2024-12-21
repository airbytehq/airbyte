#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping

import pendulum

from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator


class AWSAuthenticator(Oauth2Authenticator):
    def __init__(self, host: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.host = host

    def get_auth_header(self) -> Mapping[str, Any]:
        return {
            "host": self.host,
            "user-agent": "python-requests",
            "x-amz-access-token": self.get_access_token(),
            "x-amz-date": pendulum.now("utc").strftime("%Y%m%dT%H%M%SZ"),
        }
