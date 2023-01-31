#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from requests.auth import HTTPBasicAuth
from source_freshdesk.streams import (
    Agents,
    BusinessHours,
    CannedResponseFolders,
    CannedResponses,
    Companies,
    Contacts,
    Conversations,
    DiscussionCategories,
    DiscussionComments,
    DiscussionForums,
    DiscussionTopics,
    EmailConfigs,
    EmailMailboxes,
    Groups,
    Products,
    Roles,
    SatisfactionRatings,
    ScenarioAutomations,
    Settings,
    Skills,
    SlaPolicies,
    SolutionArticles,
    SolutionCategories,
    SolutionFolders,
    Surveys,
    TicketFields,
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
    @staticmethod
    def _get_stream_kwargs(config: Mapping[str, Any]) -> dict:
        return {"authenticator": FreshdeskAuth(config["api_key"]), "config": config}

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        try:
            stream = Settings(**self._get_stream_kwargs(config=config))
            return stream.availability_strategy.check_availability(stream, logger, self)
        except requests.HTTPError as error:
            body = error.response.json()
            error_msg = f"{body.get('code')}: {body.get('message')}"
        except Exception as error:
            error_msg = repr(error)

        return False, error_msg

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            Agents(**self._get_stream_kwargs(config)),
            BusinessHours(**self._get_stream_kwargs(config)),
            CannedResponseFolders(**self._get_stream_kwargs(config)),
            CannedResponses(**self._get_stream_kwargs(config)),
            Companies(**self._get_stream_kwargs(config)),
            Contacts(**self._get_stream_kwargs(config)),
            Conversations(**self._get_stream_kwargs(config)),
            DiscussionCategories(**self._get_stream_kwargs(config)),
            DiscussionComments(**self._get_stream_kwargs(config)),
            DiscussionForums(**self._get_stream_kwargs(config)),
            DiscussionTopics(**self._get_stream_kwargs(config)),
            EmailConfigs(**self._get_stream_kwargs(config)),
            EmailMailboxes(**self._get_stream_kwargs(config)),
            Groups(**self._get_stream_kwargs(config)),
            Products(**self._get_stream_kwargs(config)),
            Roles(**self._get_stream_kwargs(config)),
            ScenarioAutomations(**self._get_stream_kwargs(config)),
            Settings(**self._get_stream_kwargs(config)),
            Skills(**self._get_stream_kwargs(config)),
            SlaPolicies(**self._get_stream_kwargs(config)),
            SolutionArticles(**self._get_stream_kwargs(config)),
            SolutionCategories(**self._get_stream_kwargs(config)),
            SolutionFolders(**self._get_stream_kwargs(config)),
            TimeEntries(**self._get_stream_kwargs(config)),
            TicketFields(**self._get_stream_kwargs(config)),
            Tickets(**self._get_stream_kwargs(config)),
            SatisfactionRatings(**self._get_stream_kwargs(config)),
            Surveys(**self._get_stream_kwargs(config)),
        ]
