#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import requests.exceptions
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .streams import (
    AccessCheck,
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
        def all_streams_accessible():
            access_check_stream = AccessCheck(authenticator=authenticator)
            slice_ = next(iter(access_check_stream.stream_slices(sync_mode=SyncMode.full_refresh)))
            try:
                list(access_check_stream.read_records(stream_slice=slice_, sync_mode=SyncMode.full_refresh))
            except requests.exceptions.RequestException as e:
                if e.response.status_code == requests.codes.UNAUTHORIZED:
                    return False
                raise
            else:
                return True

        authenticator = TokenAuthenticator(token=config["api_key"], auth_header="Api-Key", auth_method="")
        # end date is provided for integration tests only
        start_date, end_date = config["start_date"], config.get("end_date")
        date_range = {"start_date": start_date, "end_date": end_date}
        streams = [
            Campaigns(authenticator=authenticator),
            CampaignsMetrics(authenticator=authenticator, **date_range),
            Channels(authenticator=authenticator),
            Lists(authenticator=authenticator),
            MessageTypes(authenticator=authenticator),
            Metadata(authenticator=authenticator),
            Templates(authenticator=authenticator, **date_range),
        ]
        # Iterable supports two types of Server-side api keys:
        # - read only
        # - server side
        # The first one has a limited set of supported APIs, so others are filtered out here.
        # A simple check is done - a read operation on a stream that can be accessed only via a Server side API key.
        # If read is successful - other streams should be supported as well.
        # More on this - https://support.iterable.com/hc/en-us/articles/360043464871-API-Keys-
        if all_streams_accessible():
            streams.extend(
                [
                    Users(authenticator=authenticator, **date_range),
                    ListUsers(authenticator=authenticator),
                    EmailBounce(authenticator=authenticator, **date_range),
                    EmailClick(authenticator=authenticator, **date_range),
                    EmailComplaint(authenticator=authenticator, **date_range),
                    EmailOpen(authenticator=authenticator, **date_range),
                    EmailSend(authenticator=authenticator, **date_range),
                    EmailSendSkip(authenticator=authenticator, **date_range),
                    EmailSubscribe(authenticator=authenticator, **date_range),
                    EmailUnsubscribe(authenticator=authenticator, **date_range),
                    PushSend(authenticator=authenticator, **date_range),
                    PushSendSkip(authenticator=authenticator, **date_range),
                    PushOpen(authenticator=authenticator, **date_range),
                    PushUninstall(authenticator=authenticator, **date_range),
                    PushBounce(authenticator=authenticator, **date_range),
                    WebPushSend(authenticator=authenticator, **date_range),
                    WebPushClick(authenticator=authenticator, **date_range),
                    WebPushSendSkip(authenticator=authenticator, **date_range),
                    InAppSend(authenticator=authenticator, **date_range),
                    InAppOpen(authenticator=authenticator, **date_range),
                    InAppClick(authenticator=authenticator, **date_range),
                    InAppClose(authenticator=authenticator, **date_range),
                    InAppDelete(authenticator=authenticator, **date_range),
                    InAppDelivery(authenticator=authenticator, **date_range),
                    InAppSendSkip(authenticator=authenticator, **date_range),
                    InboxSession(authenticator=authenticator, **date_range),
                    InboxMessageImpression(authenticator=authenticator, **date_range),
                    SmsSend(authenticator=authenticator, **date_range),
                    SmsBounce(authenticator=authenticator, **date_range),
                    SmsClick(authenticator=authenticator, **date_range),
                    SmsReceived(authenticator=authenticator, **date_range),
                    SmsSendSkip(authenticator=authenticator, **date_range),
                    SmsUsageInfo(authenticator=authenticator, **date_range),
                    Purchase(authenticator=authenticator, **date_range),
                    CustomEvent(authenticator=authenticator, **date_range),
                    HostedUnsubscribeClick(authenticator=authenticator, **date_range),
                    Events(authenticator=authenticator),
                ]
            )
        return streams
