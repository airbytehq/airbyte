#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from urllib.parse import urljoin
import requests
from typing import Any, List, Mapping, Optional, Tuple
from requests.auth import AuthBase, HTTPBasicAuth

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_freshdesk.streams import Agents, Companies, Contacts, Conversations, Groups, Roles, SatisfactionRatings, Skills, Surveys, Tickets, TimeEntries


class HTTPBasicAuthNoPassword(HTTPBasicAuth):

    def __init__(self, username: str) -> None:
        """
        Freshdesk expects the user to provide an api_key. Any string can be used as password:
        https://developers.freshdesk.com/api/#authentication
        """
        super().__init__(username=username, password="unused_with_api_key")


class SourceFreshdesk(AbstractSource):

    def _create_authenticator(self, api_key: str) -> AuthBase:
        return HTTPBasicAuthNoPassword(username=api_key)

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        alive = True
        error_msg = None
        try:
            url = urljoin(f"https://{config['domain'].rstrip('/')}", "/api/v2/settings/helpdesk")
            response = requests.get(url=url, auth=self._create_authenticator(config["api_key"]))
            if not response.ok:
                alive = False
                try:
                    body = response.json()
                    error_msg = f"{body.get('code')}: {body['message']}"
                except ValueError:
                    error_msg = "Invalid credentials"
        except Exception as error:
            alive = False
            error_msg = repr(error)

        return alive, error_msg
    
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = self._create_authenticator(config["api_key"])
        stream_kwargs = {"authenticator": authenticator, "config": config}
        return [
            Agents(**stream_kwargs),
            Companies(**stream_kwargs),
            Contacts(**stream_kwargs),
            Conversations(**stream_kwargs),
            Groups(**stream_kwargs),
            Roles(**stream_kwargs),
            Skills(**stream_kwargs),
            Surveys(**stream_kwargs),
            TimeEntries(**stream_kwargs),
            Tickets(**stream_kwargs),
            SatisfactionRatings(**stream_kwargs)
        ]
