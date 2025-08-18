#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from typing import Any, List, Mapping, Optional

import pendulum

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream
from source_twilio.auth import HttpBasicAuthenticator
from source_twilio.streams import (
    Addresses,
    Alerts,
    Applications,
    AvailablePhoneNumberCountries,
    AvailablePhoneNumbersLocal,
    AvailablePhoneNumbersMobile,
    AvailablePhoneNumbersTollFree,
    Calls,
    ConferenceParticipants,
    Conferences,
    ConversationMessages,
    ConversationParticipants,
    DependentPhoneNumbers,
    Executions,
    IncomingPhoneNumbers,
    Keys,
    MessageMedia,
    Messages,
    OutgoingCallerIds,
    Queues,
    Recordings,
    Roles,
    Step,
    Transcriptions,
    UsageRecords,
    UsageTriggers,
    UserConversations,
)


RETENTION_WINDOW_LIMIT = 400


class SourceTwilio(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = HttpBasicAuthenticator(
            (
                config["account_sid"],
                config["auth_token"],
            ),
        )
        full_refresh_stream_kwargs = {"authenticator": auth}
        incremental_stream_kwargs = {
            "authenticator": auth,
            "start_date": config["start_date"],
            "lookback_window": config.get("lookback_window", 0),
            "slice_step_map": config.get("slice_step_map", {}),
        }

        # Fix for `Date range specified in query is partially or entirely outside of retention window of 400 days`
        # See: https://app.zenhub.com/workspaces/python-connectors-6262f8b593bb82001df56c65/issues/airbytehq/airbyte/10418
        incremental_stream_kwargs_message_stream = dict(**incremental_stream_kwargs)
        if pendulum.now().diff(pendulum.parse(config["start_date"])).days >= RETENTION_WINDOW_LIMIT:
            incremental_stream_kwargs_message_stream["start_date"] = (
                pendulum.now() - datetime.timedelta(days=RETENTION_WINDOW_LIMIT - 1)
            ).to_iso8601_string()

        streams = super().streams(config=config)
        streams += [
            Addresses(**full_refresh_stream_kwargs),
            Alerts(**incremental_stream_kwargs),
            Applications(**full_refresh_stream_kwargs),
            AvailablePhoneNumberCountries(**full_refresh_stream_kwargs),
            AvailablePhoneNumbersLocal(**full_refresh_stream_kwargs),
            AvailablePhoneNumbersMobile(**full_refresh_stream_kwargs),
            AvailablePhoneNumbersTollFree(**full_refresh_stream_kwargs),
            Calls(**incremental_stream_kwargs),
            ConferenceParticipants(**full_refresh_stream_kwargs),
            Conferences(**incremental_stream_kwargs),
            ConversationMessages(**full_refresh_stream_kwargs),
            ConversationParticipants(**full_refresh_stream_kwargs),
            DependentPhoneNumbers(**full_refresh_stream_kwargs),
            Executions(**full_refresh_stream_kwargs),
            IncomingPhoneNumbers(**full_refresh_stream_kwargs),
            Keys(**full_refresh_stream_kwargs),
            MessageMedia(**incremental_stream_kwargs_message_stream),
            Messages(**incremental_stream_kwargs_message_stream),
            OutgoingCallerIds(**full_refresh_stream_kwargs),
            Queues(**full_refresh_stream_kwargs),
            Recordings(**incremental_stream_kwargs),
            Roles(**full_refresh_stream_kwargs),
            Step(**full_refresh_stream_kwargs),
            Transcriptions(**full_refresh_stream_kwargs),
            UsageRecords(**incremental_stream_kwargs),
            UsageTriggers(**full_refresh_stream_kwargs),
            UserConversations(**full_refresh_stream_kwargs),
        ]
        return streams
