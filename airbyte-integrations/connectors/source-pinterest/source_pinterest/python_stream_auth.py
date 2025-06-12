#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Tuple

import pendulum
import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.airbyte_secrets_utils import add_to_secrets


class PinterestOauthAuthenticator(Oauth2Authenticator):
    """
    Custom implementation of Oauth2Authenticator that allows injection of auth headers in call to refresh access token
    """

    def __init__(
        self,
        token_refresh_endpoint: str,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        scopes: List[str] = None,
        token_expiry_date: pendulum.DateTime = None,
        token_expiry_date_format: str = None,
        access_token_name: str = "access_token",
        expires_in_name: str = "expires_in",
        refresh_request_body: Mapping[str, Any] = None,
        grant_type: str = "refresh_token",
        token_expiry_is_time_of_expiration: bool = False,
        refresh_token_error_status_codes: Tuple[int, ...] = (),
        refresh_token_error_key: str = "",
        refresh_token_error_values: Tuple[str, ...] = (),
        refresh_access_token_headers: Optional[Mapping[str, Any]] = None,
    ):
        super().__init__(
            token_refresh_endpoint,
            client_id,
            client_secret,
            refresh_token,
            scopes,
            token_expiry_date,
            token_expiry_date_format,
            access_token_name,
            expires_in_name,
            refresh_request_body,
            grant_type,
            token_expiry_is_time_of_expiration,
            refresh_token_error_status_codes,
            refresh_token_error_key,
            refresh_token_error_values,
        )
        self._refresh_access_token_headers = refresh_access_token_headers

    def _get_refresh_access_token_response(self) -> Any:
        try:
            headers = self._refresh_access_token_headers or {}
            response = requests.request(
                method="POST",
                url=self.get_token_refresh_endpoint(),
                data=self.build_refresh_request_body(),
                headers=headers,
            )
            if response.ok:
                response_json = response.json()
                access_key = response_json.get(self.get_access_token_name())
                if not access_key:
                    raise Exception(f"Token refresh API response was missing access token {self.get_access_token_name()}")
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
                message = "Refresh token is invalid or expired. Please re-authenticate from Sources/<your source>/Settings."
                raise AirbyteTracedException(internal_message=message, message=message, failure_type=FailureType.config_error)
            raise
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e
