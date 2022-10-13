#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .streams import (
    Campaigns,
    CampaignsMetrics,
    Channels,
    CustomEvent,
    EmailBounce,
    EmailClick,
    EmailComplaint,
    EmailOpen,
    EmailSend,
    EmailSendSkip,
    EmailSubscribe,
    EmailUnsubscribe,
    Events,
    HostedUnsubscribeClick,
    InAppClick,
    InAppClose,
    InAppDelete,
    InAppDelivery,
    InAppOpen,
    InAppSend,
    InAppSendSkip,
    InboxMessageImpression,
    InboxSession,
    Lists,
    ListUsers,
    MessageTypes,
    Metadata,
    Purchase,
    PushBounce,
    PushOpen,
    PushSend,
    PushSendSkip,
    PushUninstall,
    SmsBounce,
    SmsClick,
    SmsReceived,
    SmsSend,
    SmsSendSkip,
    SmsUsageInfo,
    Templates,
    Users,
    WebPushClick,
    WebPushSend,
    WebPushSendSkip,
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
            PushSend(authenticator=authenticator, start_date=config["start_date"]),
            PushSendSkip(authenticator=authenticator, start_date=config["start_date"]),
            PushOpen(authenticator=authenticator, start_date=config["start_date"]),
            PushUninstall(authenticator=authenticator, start_date=config["start_date"]),
            PushBounce(authenticator=authenticator, start_date=config["start_date"]),
            WebPushSend(authenticator=authenticator, start_date=config["start_date"]),
            WebPushClick(authenticator=authenticator, start_date=config["start_date"]),
            WebPushSendSkip(authenticator=authenticator, start_date=config["start_date"]),
            InAppSend(authenticator=authenticator, start_date=config["start_date"]),
            InAppOpen(authenticator=authenticator, start_date=config["start_date"]),
            InAppClick(authenticator=authenticator, start_date=config["start_date"]),
            InAppClose(authenticator=authenticator, start_date=config["start_date"]),
            InAppDelete(authenticator=authenticator, start_date=config["start_date"]),
            InAppDelivery(authenticator=authenticator, start_date=config["start_date"]),
            InAppSendSkip(authenticator=authenticator, start_date=config["start_date"]),
            InboxSession(authenticator=authenticator, start_date=config["start_date"]),
            InboxMessageImpression(authenticator=authenticator, start_date=config["start_date"]),
            SmsSend(authenticator=authenticator, start_date=config["start_date"]),
            SmsBounce(authenticator=authenticator, start_date=config["start_date"]),
            SmsClick(authenticator=authenticator, start_date=config["start_date"]),
            SmsReceived(authenticator=authenticator, start_date=config["start_date"]),
            SmsSendSkip(authenticator=authenticator, start_date=config["start_date"]),
            SmsUsageInfo(authenticator=authenticator, start_date=config["start_date"]),
            Purchase(authenticator=authenticator, start_date=config["start_date"]),
            CustomEvent(authenticator=authenticator, start_date=config["start_date"]),
            HostedUnsubscribeClick(authenticator=authenticator, start_date=config["start_date"]),
            Events(authenticator=authenticator),
            Lists(authenticator=authenticator),
            ListUsers(authenticator=authenticator),
            MessageTypes(authenticator=authenticator),
            Metadata(authenticator=authenticator),
            Templates(authenticator=authenticator, start_date=config["start_date"]),
            Users(authenticator=authenticator, start_date=config["start_date"]),
        ]
