#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import logging
from dataclasses import dataclass

import backoff
import requests
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException

logger = logging.getLogger("airbyte")


@dataclass
class PayPalOauth2Authenticator(DeclarativeOauth2Authenticator):
    """Request example for API token extraction:
    For `old_config` scenario:
        curl -v POST https://api-m.sandbox.paypal.com/v1/oauth2/token \
        -H "Accept: application/json" \
        -H "Accept-Language: en_US" \
        -u "CLIENT_ID:SECRET" \
        -d "grant_type=client_credentials"
    """

    # config: Mapping[str, Any]
    # client_id: Union[InterpolatedString, str]
    # client_secret: Union[InterpolatedString, str]
    # refresh_request_body: Optional[Mapping[str, Any]] = None
    # token_refresh_endpoint: Union[InterpolatedString, str]
    # grant_type: Union[InterpolatedString, str] = "refresh_token"
    # expires_in_name: Union[InterpolatedString, str] = "expires_in"
    # access_token_name: Union[InterpolatedString, str] = "access_token"
    # parameters: InitVar[Mapping[str, Any]]

    def get_headers(self):
        basic_auth = base64.b64encode(bytes(f"{self.get_client_id()}:{self.get_client_secret()}", "utf-8")).decode("utf-8")
        return {"Authorization": f"Basic {basic_auth}"}

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
                method="POST", url=self.get_token_refresh_endpoint(), data=self.build_refresh_request_body(), headers=self.get_headers()
            )
            self._log_response(response)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if e.response.status_code == 429 or e.response.status_code >= 500:
                raise DefaultBackoffException(request=e.response.request, response=e.response)
            raise
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e
