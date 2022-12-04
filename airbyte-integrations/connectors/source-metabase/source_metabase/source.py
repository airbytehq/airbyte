#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterator, List, Mapping, MutableMapping, Tuple

import requests
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from source_metabase.streams import Activity, Cards, Collections, Dashboards, Users

API_URL = "instance_api_url"
USERNAME = "username"
PASSWORD = "password"
SESSION_TOKEN = "session_token"


class MetabaseAuth(HttpAuthenticator):
    def __init__(self, logger: logging.Logger, config: Mapping[str, Any]):
        self.need_session_close = False
        self.session_token = ""
        self.logger = logger
        self.api_url = config[API_URL]
        if USERNAME in config and PASSWORD in config:
            self.username = config[USERNAME]
            self.password = config[PASSWORD]
        if SESSION_TOKEN in config:
            self.session_token = config[SESSION_TOKEN]
        elif USERNAME in config and PASSWORD in config:
            self.session_token = self.get_new_session_token(config[USERNAME], config[PASSWORD])
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
            self.logger.info(f"New session token generated for {username}")
        else:
            raise ConnectionError(f"Failed to retrieve new session token, response code {response.status_code} because {response.reason}")
        return self.session_token

    def has_valid_token(self) -> bool:
        try:
            response = requests.get(f"{self.api_url}user/current", headers=self.get_auth_header())
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                self.logger.warn(f"Unable to connect to Metabase source due to {str(e)}, retrying with a new session_token...")
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


class SourceMetabase(AbstractSource):
    def __init__(self):
        self.session = None

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        session = None
        try:
            session = MetabaseAuth(logger, config)
            return session.has_valid_token(), None
        except Exception as e:
            return False, e
        finally:
            if session:
                session.close_session()

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        self.session = MetabaseAuth(logging.getLogger("airbyte"), config)
        if not self.session.has_valid_token():
            raise ConnectionError("Failed to connect to source")
        args = {"authenticator": self.session, API_URL: config[API_URL]}
        return [
            Activity(**args),
            Cards(**args),
            Collections(**args),
            Dashboards(**args),
            Users(**args),
        ]

    # We override the read method to make sure we close the metabase session and logout
    # so we don't keep too many active session_token active.
    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: MutableMapping[str, Any] = None,
    ) -> Iterator[AirbyteMessage]:
        try:
            yield from super().read(logger, config, catalog, state)
        finally:
            self.close_session()

    def close_session(self):
        if self.session:
            self.session.close_session()
