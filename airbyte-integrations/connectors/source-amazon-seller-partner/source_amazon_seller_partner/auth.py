#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import backoff
import pendulum
from typing import Any, Mapping, Tuple
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException

logger = logging.getLogger("airbyte")

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

    @backoff.on_exception(
        backoff.expo,
        DefaultBackoffException,
        on_backoff=lambda details: logger.info(
            f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        ),
        max_time=300,
    )
    def refresh_access_token(self) -> Tuple[str, int]:
        """
        returns a tuple of (access_token, token_lifespan_in_seconds). 
        Add 5 minute buffer to access token refresh. 
        """
        access_token, expires_in = super().refresh_access_token()
        return access_token, (expires_in - 300)
