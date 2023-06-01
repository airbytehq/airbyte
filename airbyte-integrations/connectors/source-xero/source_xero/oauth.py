#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import logging
from typing import Any, Mapping

import backoff
import requests
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from airbyte_cdk.sources.streams.http.requests_native_auth import SingleUseRefreshTokenOauth2Authenticator

logger = logging.getLogger("airbyte")


class XeroSingleUseRefreshTokenOauth2Authenticator(SingleUseRefreshTokenOauth2Authenticator):
    """
    Generates OAuth2.0 access tokens from an OAuth2.0 refresh token and client credentials.
    The generated access token is attached to each request via the Authorization header.
    """

    @backoff.on_exception(
        backoff.expo,
        DefaultBackoffException,
        on_backoff=lambda details: logger.info(
            f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        ),
        max_time=300,
    )
    def _get_refresh_access_token_response(self):
        try:
            response = requests.request(
                method="POST",
                url=self.get_token_refresh_endpoint(),
                data=self.build_refresh_request_body(),
                headers=self.build_refresh_request_headers(),
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if e.response.status_code == 429 or e.response.status_code >= 500:
                raise DefaultBackoffException(request=e.response.request, response=e.response)
            raise
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e

    def build_refresh_request_body(self) -> Mapping[str, Any]:
        payload = super().build_refresh_request_body()
        payload.pop("client_id", None)
        payload.pop("client_secret", None)
        return payload

    def build_refresh_request_headers(self) -> Mapping[str, Any]:
        return {"Authorization": "Basic " + str(base64.b64encode(bytes(self._client_id + ":" + self._client_secret, "utf-8")), "utf-8")}
