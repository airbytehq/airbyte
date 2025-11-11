#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import abstractmethod
from datetime import timedelta
from json import JSONDecodeError
from typing import Any, List, Mapping, MutableMapping, Optional, Tuple, Union

import backoff
import requests
from requests.auth import AuthBase

from airbyte_cdk.models import FailureType, Level
from airbyte_cdk.sources.http_logger import format_http_message
from airbyte_cdk.sources.message import MessageRepository, NoopMessageRepository
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.airbyte_secrets_utils import add_to_secrets
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime, ab_datetime_now, ab_datetime_parse

from ..exceptions import DefaultBackoffException

logger = logging.getLogger("airbyte")
_NOOP_MESSAGE_REPOSITORY = NoopMessageRepository()


class ResponseKeysMaxRecurtionReached(AirbyteTracedException):
    """
    Raised when the max level of recursion is reached, when trying to
    find-and-get the target key, during the `_make_handled_request`
    """


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

    @property
    def _is_access_token_flow(self) -> bool:
        return self.get_token_refresh_endpoint() is None and self.access_token is not None

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

    def get_auth_header(self) -> Mapping[str, Any]:
        """HTTP header to set on the requests"""
        token = self.access_token if self._is_access_token_flow else self.get_access_token()
        return {"Authorization": f"Bearer {token}"}

    def get_access_token(self) -> str:
        """Returns the access token"""
        if self.token_has_expired():
            token, expires_in = self.refresh_access_token()
            self.access_token = token
            self.set_token_expiry_date(expires_in)

        return self.access_token

    def token_has_expired(self) -> bool:
        """Returns True if the token is expired"""
        return ab_datetime_now() > self.get_token_expiry_date()

    def build_refresh_request_body(self) -> Mapping[str, Any]:
        """
        Returns the request body to set on the refresh request

        Override to define additional parameters
        """
        payload: MutableMapping[str, Any] = {
            self.get_grant_type_name(): self.get_grant_type(),
            self.get_client_id_name(): self.get_client_id(),
            self.get_client_secret_name(): self.get_client_secret(),
            self.get_refresh_token_name(): self.get_refresh_token(),
        }

        if self.get_scopes():
            payload["scopes"] = self.get_scopes()

        if self.get_refresh_request_body():
            for key, val in self.get_refresh_request_body().items():
                # We defer to existing oauth constructs over custom configured fields
                if key not in payload:
                    payload[key] = val

        return payload

    def build_refresh_request_headers(self) -> Mapping[str, Any] | None:
        """
        Returns the request headers to set on the refresh request

        """
        headers = self.get_refresh_request_headers()
        return headers if headers else None

    def refresh_access_token(self) -> Tuple[str, AirbyteDateTime]:
        """
        Returns the refresh token and its expiration datetime

        :return: a tuple of (access_token, token_lifespan)
        """
        response_json = self._make_handled_request()
        self._ensure_access_token_in_response(response_json)

        return (
            self._extract_access_token(response_json),
            self._extract_token_expiry_date(response_json),
        )

    # ----------------
    # PRIVATE METHODS
    # ----------------

    def _default_token_expiry_date(self) -> AirbyteDateTime:
        """
        Returns the default token expiry date
        """
        # 1 hour was chosen as a middle ground to avoid unnecessary frequent refreshes and token expiration
        default_token_expiry_duration_hours = 1  # 1 hour
        return ab_datetime_now() + timedelta(hours=default_token_expiry_duration_hours)

    def _wrap_refresh_token_exception(
        self, exception: requests.exceptions.RequestException
    ) -> bool:
        """
        Wraps and handles exceptions that occur during the refresh token process.

        This method checks if the provided exception is related to a refresh token error
        by examining the response status code and specific error content.

        Args:
            exception (requests.exceptions.RequestException): The exception raised during the request.

        Returns:
            bool: True if the exception is related to a refresh token error, False otherwise.
        """
        try:
            if exception.response is not None:
                exception_content = exception.response.json()
            else:
                return False
        except JSONDecodeError:
            return False
        return (
            exception.response.status_code in self._refresh_token_error_status_codes
            and exception_content.get(self._refresh_token_error_key)
            in self._refresh_token_error_values
        )

    @backoff.on_exception(
        backoff.expo,
        DefaultBackoffException,
        on_backoff=lambda details: logger.info(
            f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        ),
        max_time=300,
    )
    def _make_handled_request(self) -> Any:
        """
        Makes a handled HTTP request to refresh an OAuth token.

        This method sends a POST request to the token refresh endpoint with the necessary
        headers and body to obtain a new access token. It handles various exceptions that
        may occur during the request and logs the response for troubleshooting purposes.

        Returns:
            Mapping[str, Any]: The JSON response from the token refresh endpoint.

        Raises:
            DefaultBackoffException: If the response status code is 429 (Too Many Requests)
                                     or any 5xx server error.
            AirbyteTracedException: If the refresh token is invalid or expired, prompting
                                    re-authentication.
            Exception: For any other exceptions that occur during the request.
        """
        try:
            response = requests.request(
                method="POST",
                url=self.get_token_refresh_endpoint(),  # type: ignore # returns None, if not provided, but str | bytes is expected.
                data=self.build_refresh_request_body(),
                headers=self.build_refresh_request_headers(),
            )

            if not response.ok:
                # log the response even if the request failed for troubleshooting purposes
                self._log_response(response)
                response.raise_for_status()

            response_json = response.json()

            try:
                # extract the access token and add to secrets to avoid logging the raw value
                access_key = self._extract_access_token(response_json)
                if access_key:
                    add_to_secrets(access_key)
            except ResponseKeysMaxRecurtionReached as e:
                # could not find the access token in the response, so do nothing
                pass

            self._log_response(response)

            return response_json
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                if e.response.status_code == 429 or e.response.status_code >= 500:
                    raise DefaultBackoffException(
                        request=e.response.request,
                        response=e.response,
                        failure_type=FailureType.transient_error,
                    )
            if self._wrap_refresh_token_exception(e):
                message = "Refresh token is invalid or expired. Please re-authenticate from Sources/<your source>/Settings."
                raise AirbyteTracedException(
                    internal_message=message, message=message, failure_type=FailureType.config_error
                )
            raise
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e

    def _ensure_access_token_in_response(self, response_data: Mapping[str, Any]) -> None:
        """
        Ensures that the access token is present in the response data.

        This method attempts to extract the access token from the provided response data.
        If the access token is not found, it raises an exception indicating that the token
        refresh API response was missing the access token.

        Args:
            response_data (Mapping[str, Any]): The response data from which to extract the access token.

        Raises:
            Exception: If the access token is not found in the response data.
            ResponseKeysMaxRecurtionReached: If the maximum recursion depth is reached while extracting the access token.
        """
        try:
            access_key = self._extract_access_token(response_data)
            if not access_key:
                raise Exception(
                    f"Token refresh API response was missing access token {self.get_access_token_name()}"
                )
        except ResponseKeysMaxRecurtionReached as e:
            raise e

    def _parse_token_expiration_date(self, value: Union[str, int]) -> AirbyteDateTime:
        """
        Parse a string or integer token expiration date into a datetime object

        :return: expiration datetime
        """
        if self.token_expiry_is_time_of_expiration:
            if not self.token_expiry_date_format:
                raise ValueError(
                    f"Invalid token expiry date format {self.token_expiry_date_format}; a string representing the format is required."
                )
            try:
                return ab_datetime_parse(str(value))
            except ValueError as e:
                raise ValueError(f"Invalid token expiry date format: {e}")
        else:
            try:
                # Only accept numeric values (as int/float/string) when no format specified
                seconds = int(float(str(value)))
                return ab_datetime_now() + timedelta(seconds=seconds)
            except (ValueError, TypeError):
                raise ValueError(
                    f"Invalid expires_in value: {value}. Expected number of seconds when no format specified."
                )

    def _extract_access_token(self, response_data: Mapping[str, Any]) -> Any:
        """
        Extracts the access token from the given response data.

        Args:
            response_data (Mapping[str, Any]): The response data from which to extract the access token.

        Returns:
            str: The extracted access token.
        """
        return self._find_and_get_value_from_response(response_data, self.get_access_token_name())

    def _extract_refresh_token(self, response_data: Mapping[str, Any]) -> Any:
        """
        Extracts the refresh token from the given response data.

        Args:
            response_data (Mapping[str, Any]): The response data from which to extract the refresh token.

        Returns:
            str: The extracted refresh token.
        """
        return self._find_and_get_value_from_response(response_data, self.get_refresh_token_name())

    def _extract_token_expiry_date(self, response_data: Mapping[str, Any]) -> AirbyteDateTime:
        """
        Extracts the token_expiry_date, like `expires_in` or `expires_at`, etc from the given response data.

        If the token_expiry_date is not found, it will return an existing token expiry date if set, or a default token expiry date.

        Args:
            response_data (Mapping[str, Any]): The response data from which to extract the token_expiry_date.

        Returns:
            The extracted token_expiry_date or None if not found.
        """
        expires_in = self._find_and_get_value_from_response(
            response_data, self.get_expires_in_name()
        )
        if expires_in is not None:
            return self._parse_token_expiration_date(expires_in)

        # expires_in is None
        existing_expiry_date = self.get_token_expiry_date()
        if existing_expiry_date and not self.token_has_expired():
            return existing_expiry_date

        return self._default_token_expiry_date()

    def _find_and_get_value_from_response(
        self,
        response_data: Mapping[str, Any],
        key_name: str,
        max_depth: int = 5,
        current_depth: int = 0,
    ) -> Any:
        """
        Recursively searches for a specified key in a nested dictionary or list and returns its value if found.

        Args:
            response_data (Mapping[str, Any]): The response data to search through, which can be a dictionary or a list.
            key_name (str): The key to search for in the response data.
            max_depth (int, optional): The maximum depth to search for the key to avoid infinite recursion. Defaults to 5.
            current_depth (int, optional): The current depth of the recursion. Defaults to 0.

        Returns:
            Any: The value associated with the specified key if found, otherwise None.

        Raises:
            AirbyteTracedException: If the maximum recursion depth is reached without finding the key.
        """
        if current_depth > max_depth:
            # this is needed to avoid an inf loop, possible with a very deep nesting observed.
            message = f"The maximum level of recursion is reached. Couldn't find the specified `{key_name}` in the response."
            raise ResponseKeysMaxRecurtionReached(
                internal_message=message, message=message, failure_type=FailureType.config_error
            )

        if isinstance(response_data, dict):
            # get from the root level
            if key_name in response_data:
                return response_data[key_name]

            # get from the nested object
            for _, value in response_data.items():
                result = self._find_and_get_value_from_response(
                    value, key_name, max_depth, current_depth + 1
                )
                if result is not None:
                    return result

        # get from the nested array object
        elif isinstance(response_data, list):
            for item in response_data:
                result = self._find_and_get_value_from_response(
                    item, key_name, max_depth, current_depth + 1
                )
                if result is not None:
                    return result

        return None

    @property
    def _message_repository(self) -> Optional[MessageRepository]:
        """
        The implementation can define a message_repository if it wants debugging logs for HTTP requests
        """
        return _NOOP_MESSAGE_REPOSITORY

    def _log_response(self, response: requests.Response) -> None:
        """
        Logs the HTTP response using the message repository if it is available.

        Args:
            response (requests.Response): The HTTP response to log.
        """
        if self._message_repository:
            self._message_repository.log_message(
                Level.DEBUG,
                lambda: format_http_message(
                    response,
                    "Refresh token",
                    "Obtains access token",
                    self._NO_STREAM_NAME,
                    is_auxiliary=True,
                    type="AUTH",
                ),
            )

    # ----------------
    # ABSTR METHODS
    # ----------------

    @abstractmethod
    def get_token_refresh_endpoint(self) -> Optional[str]:
        """Returns the endpoint to refresh the access token"""

    @abstractmethod
    def get_client_id_name(self) -> str:
        """The client id name to authenticate"""

    @abstractmethod
    def get_client_id(self) -> str:
        """The client id to authenticate"""

    @abstractmethod
    def get_client_secret_name(self) -> str:
        """The client secret name to authenticate"""

    @abstractmethod
    def get_client_secret(self) -> str:
        """The client secret to authenticate"""

    @abstractmethod
    def get_refresh_token_name(self) -> str:
        """The refresh token name to authenticate"""

    @abstractmethod
    def get_refresh_token(self) -> Optional[str]:
        """The token used to refresh the access token when it expires"""

    @abstractmethod
    def get_scopes(self) -> List[str]:
        """List of requested scopes"""

    @abstractmethod
    def get_token_expiry_date(self) -> AirbyteDateTime:
        """Expiration date of the access token"""

    @abstractmethod
    def set_token_expiry_date(self, value: AirbyteDateTime) -> None:
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
    def get_refresh_request_headers(self) -> Mapping[str, Any]:
        """Returns the request headers to set on the refresh request"""

    @abstractmethod
    def get_grant_type(self) -> str:
        """Returns grant_type specified for requesting access_token"""

    @abstractmethod
    def get_grant_type_name(self) -> str:
        """Returns grant_type specified name for requesting access_token"""

    @property
    @abstractmethod
    def access_token(self) -> str:
        """Returns the access token"""

    @access_token.setter
    @abstractmethod
    def access_token(self, value: str) -> str:
        """Setter for the access token"""
