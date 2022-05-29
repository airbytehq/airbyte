#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from base64 import b64encode
from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator

from .streams import QualarooStream, Responses, Surveys


class QualarooAuthenticator(HttpAuthenticator):
    """
    Generate auth header for start making requests from API token and API key.
    """

    def __init__(
        self,
        key: str,
        token: str,
        auth_header: str = "Authorization",
        key_header: str = "oauth_consumer_key",
        token_header: str = "oauth_token",
    ):
        self._key = key
        self._token = b64encode(b":".join((key.encode("latin1"), token.encode("latin1")))).strip().decode("ascii")
        self.auth_header = auth_header
        self.key_header = key_header
        self.token_header = token_header

    def get_auth_header(self) -> Mapping[str, Any]:
        return {self.auth_header: f"Basic {self._token}"}


class SourceQualaroo(AbstractSource):
    """
    Source Qualaroo fetch date from web-based, Kanban-style, list-making application.
    """

    @staticmethod
    def _get_authenticator(config: dict) -> QualarooAuthenticator:
        key, token = config["key"], config["token"]
        return QualarooAuthenticator(token=token, key=key)

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Testing connection availability for the connector by granting the credentials.
        """

        try:
            url = f"{QualarooStream.url_base}nudges"

            authenticator = self._get_authenticator(config)

            response = requests.get(url, headers=authenticator.get_auth_header())

            response.raise_for_status()
            available_surveys = {row.get("id") for row in response.json()}
            for survey_id in config.get("survey_ids", []):
                if survey_id not in available_surveys:
                    return False, f"survey_id {survey_id} not found"
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        args = {}
        # convert start_date to epoch time for qualaroo API
        args["start_date"] = pendulum.parse(config["start_date"]).strftime("%s")
        args["survey_ids"] = config.get("survey_ids", [])
        args["authenticator"] = self._get_authenticator(config)
        return [Surveys(**args), Responses(**args)]
