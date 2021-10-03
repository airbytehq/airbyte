#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_twilio.auth import HttpBasicAuthenticator
from source_twilio.streams import (
    Accounts,
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
    DependentPhoneNumbers,
    IncomingPhoneNumbers,
    Keys,
    MessageMedia,
    Messages,
    OutgoingCallerIds,
    Queues,
    Recordings,
    Transcriptions,
    UsageRecords,
    UsageTriggers,
)


class SourceTwilio(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            auth = HttpBasicAuthenticator(
                (
                    config["account_sid"],
                    config["auth_token"],
                ),
            )
            accounts_gen = Accounts(authenticator=auth).read_records(sync_mode=SyncMode.full_refresh)
            next(accounts_gen)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Twilio API with the provided credentials - {repr(error)}"

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
        incremental_stream_kwargs = {"authenticator": auth, "start_date": config["start_date"]}

        streams = [
            Accounts(**full_refresh_stream_kwargs),
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
            DependentPhoneNumbers(**full_refresh_stream_kwargs),
            IncomingPhoneNumbers(**full_refresh_stream_kwargs),
            Keys(**full_refresh_stream_kwargs),
            MessageMedia(**incremental_stream_kwargs),
            Messages(**incremental_stream_kwargs),
            OutgoingCallerIds(**full_refresh_stream_kwargs),
            Queues(**full_refresh_stream_kwargs),
            Recordings(**incremental_stream_kwargs),
            Transcriptions(**full_refresh_stream_kwargs),
            UsageRecords(**incremental_stream_kwargs),
            UsageTriggers(**full_refresh_stream_kwargs),
        ]
        return streams
