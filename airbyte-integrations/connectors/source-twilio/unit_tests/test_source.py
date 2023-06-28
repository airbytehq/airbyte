#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
import requests
from source_twilio.source import SourceTwilio
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
    ConversationParticipants,
    Conversations,
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
    VerifyServices,
)


@pytest.fixture
def config():
    return {
        "account_sid": "airbyte.io",
        "auth_token": "secret",
        "start_date": "2022-01-01T00:00:00Z",
        "lookback_window": 0,
    }


TEST_INSTANCE = SourceTwilio()


@pytest.mark.parametrize(
    "exception, expected_error_msg",
    (
        (
            ConnectionError("Connection aborted"),
            "Unable to connect to Twilio API with the provided credentials - ConnectionError('Connection aborted')",
        ),
        (
            TimeoutError("Socket timed out"),
            "Unable to connect to Twilio API with the provided credentials - TimeoutError('Socket timed out')",
        ),
        (
            requests.exceptions.HTTPError("401 Client Error: Unauthorized for url: https://api.twilio.com/"),
            "Unable to connect to Twilio API with the provided credentials - "
            "HTTPError('401 Client Error: Unauthorized for url: https://api.twilio.com/')",
        ),
    ),
)
def test_check_connection_handles_exceptions(mocker, config, exception, expected_error_msg):
    mocker.patch.object(requests.Session, "send", Mock(side_effect=exception))
    status_ok, error = TEST_INSTANCE.check_connection(logger=None, config=config)
    assert not status_ok
    assert error == expected_error_msg


@pytest.mark.parametrize(
    "stream_cls",
    [
        (Accounts),
        (Addresses),
        (Alerts),
        (Applications),
        (AvailablePhoneNumberCountries),
        (AvailablePhoneNumbersLocal),
        (AvailablePhoneNumbersMobile),
        (AvailablePhoneNumbersTollFree),
        (Calls),
        (ConferenceParticipants),
        (Conferences),
        (DependentPhoneNumbers),
        (IncomingPhoneNumbers),
        (Keys),
        (MessageMedia),
        (Messages),
        (OutgoingCallerIds),
        (Queues),
        (Recordings),
        (Transcriptions),
        (UsageRecords),
        (UsageTriggers),
        (Conversations),
        (ConversationParticipants),
        (VerifyServices),
    ],
)
def test_streams(stream_cls, config):
    streams = TEST_INSTANCE.streams(config)
    for stream in streams:
        if stream_cls in streams:
            assert isinstance(stream, stream_cls)
