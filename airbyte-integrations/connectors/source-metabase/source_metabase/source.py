#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from source_metabase.streams import Cards


class MetabaseAuth(HttpAuthenticator):
    def __init__(self, session_token: str):
        self.session_token = session_token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-Metabase-Session": self.session_token}


class SourceMetabase(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            authenticator = MetabaseAuth(config["session_token"])
            api_url = config["instance_api_url"]
            try:
                response = requests.get(f"{api_url}user/current", headers=authenticator.get_auth_header())
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    logger.info(str(e))
                    # TODO: retrieve new session token using username/password
                    return False, "Invalid or expired session tokens, check if session is still valid"
                else:
                    logger.info(str(e))
                    return False, f"Error while checking connection: {e}r"
            json_response = response.json()
            logger.info(f"Connection check for Metabase successful for {json_response['first_name']} {json_response['last_name']}")
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = MetabaseAuth(config["session_token"])
        args = {"authenticator": authenticator, "instance_api_url": config["instance_api_url"]}
        return [
            Cards(**args),
        ]
