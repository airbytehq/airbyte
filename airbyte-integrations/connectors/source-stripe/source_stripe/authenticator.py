#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from datetime import datetime, timedelta
from typing import Tuple, Union

from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator


class StripeOauth2Authenticator(Oauth2Authenticator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def refresh_access_token(self) -> Tuple[str, Union[str, int]]:
        """
        Returns the refresh token and its expiration datetime

        :return: a tuple of (access_token, token_lifespan)
        """
        expires_in = (datetime.now() + timedelta(seconds=3600)).timestamp()
        response_json = self._get_refresh_access_token_response()

        return response_json[self.get_access_token_name()], expires_in
