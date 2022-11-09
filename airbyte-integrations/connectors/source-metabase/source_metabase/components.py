#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import dataclass
from typing import Any, Mapping

import requests
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from dataclasses_jsonschema import JsonSchemaMixin

API_URL_CONFIG_KEY = "instance_api_url"
USERNAME_CONFIG_KEY = "username"
PASSWORD_CONFIG_KEY = "password"
SESSION_TOKEN_CONFIG_KEY = "session_token"


@dataclass
class MetabaseAuth(HttpAuthenticator, JsonSchemaMixin):
    def __init__(self, config: Mapping[str, Any], options: Mapping[str, Any]):
        self.need_session_close = False
        self.session_token = ""
        self.logger = logging.getLogger("airbyte")
        self.api_url = config[API_URL_CONFIG_KEY]
        if USERNAME_CONFIG_KEY in config and PASSWORD_CONFIG_KEY in config:
            self.username = config[USERNAME_CONFIG_KEY]
            self.password = config[PASSWORD_CONFIG_KEY]
        if SESSION_TOKEN_CONFIG_KEY in config:
            self.session_token = config[SESSION_TOKEN_CONFIG_KEY]
        elif USERNAME_CONFIG_KEY in config and PASSWORD_CONFIG_KEY in config:
            self.session_token = self.get_new_session_token(config[USERNAME_CONFIG_KEY], config[PASSWORD_CONFIG_KEY])
        else:
            raise KeyError("Required parameters (username/password pair or session_token) not found")
        # TODO: Try to retrieve latest session_token stored in some state message?

    def get_new_session_token(self, username: str, password: str) -> str:
        response = requests.post(
            f"{self.api_url}session", headers={"Content-Type": "application/json"}, json={"username": username, "password": password}
        )
        response.raise_for_status()
        if response.ok:
            self.session_token = response.json()["id"]
            self.need_session_close = True
        else:
            raise ConnectionError(f"Failed to retrieve new session token, response code {response.status_code} because {response.reason}")
        return self.session_token

    def has_valid_token(self) -> bool:
        try:
            response = requests.get(f"{self.api_url}user/current", headers=self.get_auth_header())
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == requests.codes["unauthorized"]:
                self.logger.warning(f"Unable to connect to Metabase source due to {str(e)}, retrying with a new session_token...")
                self.get_new_session_token(self.username, self.password)
                response = requests.get(f"{self.api_url}user/current", headers=self.get_auth_header())
                response.raise_for_status()
            else:
                raise ConnectionError(f"Error while checking connection: {e}")
        if response.ok:
            json_response = response.json()
            self.logger.info(
                f"Connection check for Metabase successful for {json_response['common_name']} login at {json_response['last_login']}"
            )
            return True
        else:
            raise ConnectionError(f"Failed to retrieve new session token, response code {response.status_code} because {response.reason}")

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-Metabase-Session": self.session_token}

    def close_session(self):
        if self.need_session_close:
            response = requests.delete(
                f"{self.api_url}session", headers=self.get_auth_header(), json={"metabase-session-id": self.session_token}
            )
            response.raise_for_status()
            if response.ok:
                self.logger.info("Session successfully closed")
            else:
                self.logger.info(f"Unable to close session {response.status_code}: {response.reason}")
        else:
            self.logger.info("Session was not opened by this connector.")
