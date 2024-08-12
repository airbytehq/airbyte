#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Optional

from airbyte_cdk.models import AirbyteStreamStatus


def assert_stream_did_not_run(output, stream_name: str, expected_error_message_pattern: Optional[str]=None):
    # right now, no stream status AirbyteStreamStatus.RUNNING means stream not running
    expected = [
        AirbyteStreamStatus.STARTED,
        AirbyteStreamStatus.COMPLETE,
    ]

    assert output.get_stream_statuses(stream_name) == expected
    assert output.records == []

    if expected_error_message_pattern:
        def contains_substring(message, expected_message_pattern):
            return expected_message_pattern in message.log.message

        # Use any to check if any message contains the substring
        found = any(contains_substring(message, expected_error_message_pattern) for message in output.logs)
        assert found, f"Expected message '{expected_error_message_pattern}' not found in logs."

