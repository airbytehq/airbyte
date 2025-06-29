#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import time
from dataclasses import dataclass
from typing import Any, ClassVar, List, Mapping

import jwt
import requests

from .logger import Logger


TOKEN_TTL = 3600


@dataclass
class GoogleApi:
    """
    Simple Google API client
    """

    logger: ClassVar[Logger] = Logger()

    config: Mapping[str, Any]
    scopes: List[str]
    _access_token: str = None

    def get(self, url: str, params: Mapping = None) -> Mapping[str, Any]:
        """Sends a GET request"""
        token = self.get_access_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "X-Goog-User-Project": self.project_id}
        # Making a get request
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, url: str, json: Mapping = None, params: Mapping = None) -> Mapping[str, Any]:
        """Sends a POST request"""
        token = self.get_access_token()

        headers = {"Authorization": f"Bearer {token}", "X-Goog-User-Project": self.project_id}
        # Making a get request
        response = requests.post(url, headers=headers, json=json, params=params)
        try:
            response.raise_for_status()
        except Exception:
            self.logger.error(f"error body: {response.text}")
            raise
        return response.json()

    @property
    def token_uri(self):
        return self.config["token_uri"]

    @property
    def project_id(self):
        return self.config["project_id"]

    def __generate_jwt(self) -> str:
        """Generates JWT token by a service account json file and scopes"""
        now = int(time.time())
        claim = {
            "iat": now,
            "iss": self.config["client_email"],
            "scope": ",".join(self.scopes),
            "aud": self.token_uri,
            "exp": now + TOKEN_TTL,
        }
        return jwt.encode(claim, self.config["private_key"].encode(), algorithm="RS256")

    def get_access_token(self) -> str:
        """Generates an access token by a service account json file and scopes"""

        if self._access_token is None:
            self._access_token = self.__get_access_token()

        return self._access_token

    def __get_access_token(self) -> str:
        jwt = self.__generate_jwt()
        resp = requests.post(
            self.token_uri,
            data={
                "assertion": jwt,
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            },
        )
        return resp.json()["access_token"]
