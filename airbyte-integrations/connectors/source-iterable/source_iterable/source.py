#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .api import (
    Campaigns,
    CampaignsMetrics,
    Channels,
    EmailBounce,
    EmailClick,
    EmailComplaint,
    EmailOpen,
    EmailSend,
    EmailSendSkip,
    EmailSubscribe,
    EmailUnsubscribe,
    Events,
    Lists,
    ListUsers,
    MessageTypes,
    Metadata,
    Templates,
    Users,
)


class SourceIterable(AbstractSource):
    """
    Note: there are some redundant endpoints
    (e.g. [`export/userEvents`](https://api.iterable.com/api/docs#export_exportUserEvents)
    and [`events/{email}`](https://api.iterable.com/api/docs#events_User_events)).
    In this case it's better to use the one which takes params as a query param rather than as part of the url param.
    """

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            authenticator = TokenAuthenticator(token=config["api_key"], auth_header="Api-Key", auth_method="")
            list_gen = Lists(authenticator=authenticator).read_records(sync_mode=SyncMode.full_refresh)
            next(list_gen)
            return True, None
        except Exception as e:
            return False, f"Unable to connect to Iterable API with the provided credentials - {e}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(token=config["api_key"], auth_header="Api-Key", auth_method="")
        return [
            Campaigns(authenticator=authenticator),
            CampaignsMetrics(authenticator=authenticator, start_date=config["start_date"]),
            Channels(authenticator=authenticator),
            EmailBounce(authenticator=authenticator, start_date=config["start_date"]),
            EmailClick(authenticator=authenticator, start_date=config["start_date"]),
            EmailComplaint(authenticator=authenticator, start_date=config["start_date"]),
            EmailOpen(authenticator=authenticator, start_date=config["start_date"]),
            EmailSend(authenticator=authenticator, start_date=config["start_date"]),
            EmailSendSkip(authenticator=authenticator, start_date=config["start_date"]),
            EmailSubscribe(authenticator=authenticator, start_date=config["start_date"]),
            EmailUnsubscribe(authenticator=authenticator, start_date=config["start_date"]),
            Events(authenticator=authenticator),
            Lists(authenticator=authenticator),
            ListUsers(authenticator=authenticator),
            MessageTypes(authenticator=authenticator),
            Metadata(authenticator=authenticator),
            Templates(authenticator=authenticator, start_date=config["start_date"]),
            Users(authenticator=authenticator, start_date=config["start_date"]),
        ]
