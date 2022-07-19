#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import abstractmethod
from typing import Any, Mapping, MutableMapping, Tuple

import pendulum
import requests
from requests.auth import AuthBase


class AbstractOauth2Authenticator(AuthBase):
    """
    Abstract class for an OAuth authenticators that implements the OAuth token refresh flow. The authenticator
    is designed to generically perform the refresh flow without regard to how config fields are get/set by
    delegating that behavior to the classes implementing the interface.
    """

    def __call__(self, request):
        request.headers.update(self.get_auth_header())
        return request

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Authorization": f"Bearer {self.get_access_token()}"}

    def get_access_token(self):
        if self.token_has_expired():
            t0 = pendulum.now()
            token, expires_in = self.refresh_access_token()
            self.access_token = token
            self.token_expiry_date = t0.add(seconds=expires_in)

        return self.access_token

    def token_has_expired(self) -> bool:
        return pendulum.now() > self.token_expiry_date

    def get_refresh_request_body(self) -> Mapping[str, Any]:
        """Override to define additional parameters"""
        payload: MutableMapping[str, Any] = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }

        if self.scopes:
            payload["scopes"] = self.scopes

        if self.refresh_request_body:
            for key, val in self.refresh_request_body.items():
                # We defer to existing oauth constructs over custom configured fields
                if key not in payload:
                    payload[key] = val

        return payload

    def refresh_access_token(self) -> Tuple[str, int]:
        """
        returns a tuple of (access_token, token_lifespan_in_seconds)
        """
        try:
            response = requests.request(method="POST", url=self.token_refresh_endpoint, data=self.get_refresh_request_body())
            response.raise_for_status()
            response_json = response.json()
            return response_json[self.access_token_name], response_json[self.expires_in_name]
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e

    @property
    @abstractmethod
    def token_refresh_endpoint(self):
        pass

    @property
    @abstractmethod
    def client_id(self):
        pass

    @property
    @abstractmethod
    def client_secret(self):
        pass

    @property
    @abstractmethod
    def refresh_token(self):
        pass

    @property
    @abstractmethod
    def scopes(self):
        pass

    @property
    @abstractmethod
    def token_expiry_date(self):
        pass

    @token_expiry_date.setter
    @abstractmethod
    def token_expiry_date(self, value):
        pass

    @property
    @abstractmethod
    def access_token_name(self):
        pass

    @property
    @abstractmethod
    def expires_in_name(self):
        pass

    @property
    @abstractmethod
    def refresh_request_body(self):
        pass

    @property
    @abstractmethod
    def access_token(self):
        pass

    @access_token.setter
    @abstractmethod
    def access_token(self, value):
        pass
