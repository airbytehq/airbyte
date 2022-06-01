#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Optional, Tuple
from urllib.parse import urljoin

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from requests.auth import HTTPBasicAuth
from source_freshdesk.streams import (
    Agents,
    Companies,
    Contacts,
    Conversations,
    Groups,
    Roles,
    SatisfactionRatings,
    Skills,
    Surveys,
    Tickets,
    TimeEntries,
)


class FreshdeskAuth(HTTPBasicAuth):
    def __init__(self, api_key: str) -> None:
        """
        Freshdesk expects the user to provide an api_key. Any string can be used as password:
        https://developers.freshdesk.com/api/#authentication
        """
        super().__init__(username=api_key, password="unused_with_api_key")


class SourceFreshdesk(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        alive = True
        error_msg = None
        try:
            url = urljoin(f"https://{config['domain'].rstrip('/')}", "/api/v2/settings/helpdesk")
            response = requests.get(url=url, auth=FreshdeskAuth(config["api_key"]))
            response.raise_for_status()
        except requests.HTTPError as error:
            alive = False
            body = error.response.json()
            error_msg = f"{body.get('code')}: {body.get('message')}"
        except Exception as error:
            alive = False
            error_msg = repr(error)

        return alive, error_msg

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = FreshdeskAuth(config["api_key"])
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
            SatisfactionRatings(**stream_kwargs),
        ]
