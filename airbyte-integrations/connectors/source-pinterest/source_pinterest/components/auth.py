#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from base64 import standard_b64encode
from dataclasses import dataclass
from typing import Any, Mapping

import backoff
import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.airbyte_secrets_utils import add_to_secrets


logger = logging.getLogger("airbyte")


@dataclass
class PinterestOauthAuthenticator(DeclarativeOauth2Authenticator):
    """
    This class extends the DeclarativeOauth2Authenticator functionality
    and allows to pass custom headers to the refresh access token requests
    """

    def get_refresh_access_token_headers(self) -> Mapping[str, Any]:
        creds_encoded = standard_b64encode(f"{self.get_client_id()}:{self.get_client_secret()}".encode("ascii")).decode("ascii")
        return {"Authorization": f"Basic {creds_encoded}"}

    @backoff.on_exception(
        backoff.expo,
        DefaultBackoffException,
        on_backoff=lambda details: logger.info(
            f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        ),
        max_time=300,
    )
    def _get_refresh_access_token_response(self) -> Any:
        try:
            response = requests.request(
                method="POST",
                url=self.get_token_refresh_endpoint(),
                headers=self.get_refresh_access_token_headers(),
                data=self.build_refresh_request_body(),
            )
            if response.ok:
                response_json = response.json()
                access_key = response_json.get(self.get_access_token_name())
                if not access_key:
                    message = (
                        f"Token refresh API response was missing access token {self.get_access_token_name()}"
                        "Please re-authenticate from Sources/Pinterest/Settings."
                    )
                    raise AirbyteTracedException(internal_message=message, message=message, failure_type=FailureType.config_error)
                add_to_secrets(access_key)
                self._log_response(response)
                return response_json
            else:
                self._log_response(response)
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                if e.response.status_code == 429 or e.response.status_code >= 500:
                    raise DefaultBackoffException(request=e.response.request, response=e.response)
            if self._wrap_refresh_token_exception(e):
                message = "Refresh token is invalid or expired. Please re-authenticate from Sources/Pinterest/Settings."
                raise AirbyteTracedException(internal_message=message, message=message, failure_type=FailureType.config_error)
            raise
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e
