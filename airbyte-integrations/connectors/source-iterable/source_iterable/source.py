#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .streams import (
    CampaignsMetrics,
    CustomEvent,
    EmailBounce,
    EmailClick,
    EmailComplaint,
    EmailOpen,
    EmailSend,
    EmailSendSkip,
    EmailSubscribe,
    EmailUnsubscribe,
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
    WebPushClick,
    WebPushSend,
    WebPushSendSkip,
)


"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.

WARNING: Do not modify this file.
"""


# Declarative Source
class SourceIterable(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        streams = super().streams(config=config)

        authenticator = TokenAuthenticator(token=config["api_key"], auth_header="Api-Key", auth_method="")
        # end date is provided for integration tests only
        start_date, end_date = config["start_date"], config.get("end_date")
        date_range = {"start_date": start_date, "end_date": end_date}

        # TODO: migrate streams below to low code as slicer logic will be migrated to generator based
        streams.extend(
            [
                CampaignsMetrics(authenticator=authenticator, **date_range),
                Templates(authenticator=authenticator, **date_range),
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
            ]
        )
        return streams
