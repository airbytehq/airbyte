#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from typing import Any, List, Mapping, MutableMapping, Tuple, Union

import pendulum
import requests
from requests.auth import AuthBase


class AbstractOauth2Authenticator(AuthBase):
    """
    Abstract class for an OAuth authenticators that implements the OAuth token refresh flow. The authenticator
    is designed to generically perform the refresh flow without regard to how config fields are get/set by
    delegating that behavior to the classes implementing the interface.
    """

    def __call__(self, request: requests.Request) -> requests.Request:
        """Attach the HTTP headers required to authenticate on the HTTP request"""
        request.headers.update(self.get_auth_header())
        return request

    def get_auth_header(self) -> Mapping[str, Any]:
        """HTTP header to set on the requests"""
        return {"Authorization": f"Bearer {self.get_access_token()}"}

    def get_access_token(self) -> str:
        """Returns the access token"""
        if self.token_has_expired():
            current_datetime = pendulum.now()
            token, expires_in = self.refresh_access_token()
            self.access_token = token
            self.set_token_expiry_date(current_datetime, expires_in)

        return self.access_token

    def token_has_expired(self) -> bool:
        """Returns True if the token is expired"""
        return pendulum.now() > self.get_token_expiry_date()

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

        if self.get_scopes:
            payload["scopes"] = self.get_scopes()

        if self.get_refresh_request_body():
            for key, val in self.get_refresh_request_body().items():
                # We defer to existing oauth constructs over custom configured fields
                if key not in payload:
                    payload[key] = val

        return payload

    def _get_refresh_access_token_response(self):
        response = requests.request(method="POST", url=self.get_token_refresh_endpoint(), data=self.build_refresh_request_body())
        response.raise_for_status()
        return response.json()

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        Returns the refresh token and its lifespan in seconds

        :return: a tuple of (access_token, token_lifespan_in_seconds)
        """
        try:
            response_json = self._get_refresh_access_token_response()
            return response_json[self.get_access_token_name()], response_json[self.get_expires_in_name()]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e

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
    def get_refresh_token(self) -> str:
        """The token used to refresh the access token when it expires"""

    @abstractmethod
    def get_scopes(self) -> List[str]:
        """List of requested scopes"""

    @abstractmethod
    def get_token_expiry_date(self) -> pendulum.DateTime:
        """Expiration date of the access token"""

    @abstractmethod
    def set_token_expiry_date(self, initial_time: pendulum.DateTime, value: Union[str, int]):
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
