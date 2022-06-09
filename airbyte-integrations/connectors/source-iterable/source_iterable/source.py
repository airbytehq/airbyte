#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

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
            list_gen = Lists(api_key=config["api_key"]).read_records(sync_mode=SyncMode.full_refresh)
            next(list_gen)
            return True, None
        except Exception as e:
            return False, f"Unable to connect to Iterable API with the provided credentials - {e}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            Campaigns(api_key=config["api_key"]),
            CampaignsMetrics(api_key=config["api_key"], start_date=config["start_date"]),
            Channels(api_key=config["api_key"]),
            EmailBounce(api_key=config["api_key"], start_date=config["start_date"]),
            EmailClick(api_key=config["api_key"], start_date=config["start_date"]),
            EmailComplaint(api_key=config["api_key"], start_date=config["start_date"]),
            EmailOpen(api_key=config["api_key"], start_date=config["start_date"]),
            EmailSend(api_key=config["api_key"], start_date=config["start_date"]),
            EmailSendSkip(api_key=config["api_key"], start_date=config["start_date"]),
            EmailSubscribe(api_key=config["api_key"], start_date=config["start_date"]),
            EmailUnsubscribe(api_key=config["api_key"], start_date=config["start_date"]),
            Events(api_key=config["api_key"]),
            Lists(api_key=config["api_key"]),
            ListUsers(api_key=config["api_key"]),
            MessageTypes(api_key=config["api_key"]),
            Metadata(api_key=config["api_key"]),
            Templates(api_key=config["api_key"], start_date=config["start_date"]),
            Users(api_key=config["api_key"], start_date=config["start_date"]),
        ]
