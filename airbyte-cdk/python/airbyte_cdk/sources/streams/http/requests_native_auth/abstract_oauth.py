#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import abstractmethod
from json import JSONDecodeError
from typing import Any, List, Mapping, MutableMapping, Optional, Tuple, Union

import backoff
import pendulum
import requests
from airbyte_cdk.models import FailureType, Level
from airbyte_cdk.sources.http_logger import format_http_message
from airbyte_cdk.sources.message import MessageRepository, NoopMessageRepository
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.airbyte_secrets_utils import add_to_secrets
from requests.auth import AuthBase

from ..exceptions import DefaultBackoffException

logger = logging.getLogger("airbyte")
_NOOP_MESSAGE_REPOSITORY = NoopMessageRepository()


class AbstractOauth2Authenticator(AuthBase):
    """
    Abstract class for an OAuth authenticators that implements the OAuth token refresh flow. The authenticator
    is designed to generically perform the refresh flow without regard to how config fields are get/set by
    delegating that behavior to the classes implementing the interface.
    """

    _NO_STREAM_NAME = None

    def __init__(
        self,
        refresh_token_error_status_codes: Tuple[int, ...] = (),
        refresh_token_error_key: str = "",
        refresh_token_error_values: Tuple[str, ...] = (),
    ) -> None:
        """
        If all of refresh_token_error_status_codes, refresh_token_error_key, and refresh_token_error_values are set,
        then http errors with such params will be wrapped in AirbyteTracedException.
        """
        self._refresh_token_error_status_codes = refresh_token_error_status_codes
        self._refresh_token_error_key = refresh_token_error_key
        self._refresh_token_error_values = refresh_token_error_values

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Attach the HTTP headers required to authenticate on the HTTP request"""
        request.headers.update(self.get_auth_header())
        return request

    def get_auth_header(self) -> Mapping[str, Any]:
        """HTTP header to set on the requests"""
        return {"Authorization": f"Bearer {self.get_access_token()}"}

    def get_access_token(self) -> str:
        """Returns the access token"""
        if self.token_has_expired():
            token, expires_in = self.refresh_access_token()
            self.access_token = token
            self.set_token_expiry_date(expires_in)

        return self.access_token

    def token_has_expired(self) -> bool:
        """Returns True if the token is expired"""
        return pendulum.now() > self.get_token_expiry_date()  # type: ignore # this is always a bool despite what mypy thinks

    def build_refresh_request_body(self) -> Mapping[str, Any]:
        """
        Returns the request body to set on the refresh request

        Override to define additional parameters
        """
        payload: MutableMapping[str, Any] = {
            "grant_type": self.get_grant_type(),
            "client_id": self.get_client_id(),
            "client_secret": self.get_client_secret(),
            "refresh_token": self.get_refresh_token(),
        }

        if self.get_scopes():
            payload["scopes"] = self.get_scopes()

        if self.get_refresh_request_body():
            for key, val in self.get_refresh_request_body().items():
                # We defer to existing oauth constructs over custom configured fields
                if key not in payload:
                    payload[key] = val

        return payload

    def _wrap_refresh_token_exception(self, exception: requests.exceptions.RequestException) -> bool:
        try:
            if exception.response is not None:
                exception_content = exception.response.json()
            else:
                return False
        except JSONDecodeError:
            return False
        return (
            exception.response.status_code in self._refresh_token_error_status_codes
            and exception_content.get(self._refresh_token_error_key) in self._refresh_token_error_values
        )

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
            response = requests.request(method="POST", url=self.get_token_refresh_endpoint(), data=self.build_refresh_request_body())
            if response.ok:
                response_json = response.json()
                # Add the access token to the list of secrets so it is replaced before logging the response
                # An argument could be made to remove the prevous access key from the list of secrets, but unmasking values seems like a security incident waiting to happen...
                access_key = response_json.get(self.get_access_token_name())
                if not access_key:
                    raise Exception("Token refresh API response was missing access token {self.get_access_token_name()}")
                add_to_secrets(access_key)
                self._log_response(response)
                return response_json
            else:
                # log the response even if the request failed for troubleshooting purposes
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

    def refresh_access_token(self) -> Tuple[str, Union[str, int]]:
        """
        Returns the refresh token and its expiration datetime

        :return: a tuple of (access_token, token_lifespan)
        """
        response_json = self._get_refresh_access_token_response()

        return response_json[self.get_access_token_name()], response_json[self.get_expires_in_name()]

    def _parse_token_expiration_date(self, value: Union[str, int]) -> pendulum.DateTime:
        """
        Return the expiration datetime of the refresh token

        :return: expiration datetime
        """

        if self.token_expiry_is_time_of_expiration:
            if not self.token_expiry_date_format:
                raise ValueError(
                    f"Invalid token expiry date format {self.token_expiry_date_format}; a string representing the format is required."
                )
            return pendulum.from_format(str(value), self.token_expiry_date_format)
        else:
            return pendulum.now().add(seconds=int(float(value)))

    @property
    def token_expiry_is_time_of_expiration(self) -> bool:
        """
        Indicates that the Token Expiry returns the date until which the token will be valid, not the amount of time it will be valid.
        """

        return False

    @property
    def token_expiry_date_format(self) -> Optional[str]:
        """
        Format of the datetime; exists it if expires_in is returned as the expiration datetime instead of seconds until it expires
        """

        return None

    @abstractmethod
    def get_token_refresh_endpoint(self) -> str:
        """Returns the endpoint to refresh the access token"""

    @abstractmethod
    def get_client_id(self) -> str:
        """The client id to authenticate"""

    @abstractmethod
    def get_client_secret(self) -> str:
        """The client secret to authenticate"""

    @abstractmethod
    def get_refresh_token(self) -> Optional[str]:
        """The token used to refresh the access token when it expires"""

    @abstractmethod
    def get_scopes(self) -> List[str]:
        """List of requested scopes"""

    @abstractmethod
    def get_token_expiry_date(self) -> pendulum.DateTime:
        """Expiration date of the access token"""

    @abstractmethod
    def set_token_expiry_date(self, value: Union[str, int]) -> None:
        """Setter for access token expiration date"""

    @abstractmethod
    def get_access_token_name(self) -> str:
        """Field to extract access token from in the response"""

    @abstractmethod
    def get_expires_in_name(self) -> str:
        """Returns the expires_in field name"""

    @abstractmethod
    def get_refresh_request_body(self) -> Mapping[str, Any]:
        """Returns the request body to set on the refresh request"""

    @abstractmethod
    def get_grant_type(self) -> str:
        """Returns grant_type specified for requesting access_token"""

    @property
    @abstractmethod
    def access_token(self) -> str:
        """Returns the access token"""

    @access_token.setter
    @abstractmethod
    def access_token(self, value: str) -> str:
        """Setter for the access token"""

    @property
    def _message_repository(self) -> Optional[MessageRepository]:
        """
        The implementation can define a message_repository if it wants debugging logs for HTTP requests
        """
        return _NOOP_MESSAGE_REPOSITORY

    def _log_response(self, response: requests.Response) -> None:
        if self._message_repository:
            self._message_repository.log_message(
                Level.DEBUG,
                lambda: format_http_message(
                    response,
                    "Refresh token",
                    "Obtains access token",
                    self._NO_STREAM_NAME,
                    is_auxiliary=True,
                ),
            )
