#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import List

import pytest
from airbyte_cdk.models import AirbyteMessage, Type
from airbyte_protocol.models import AirbyteStreamStatus


def emits_successful_sync_status_messages(status_messages: List[AirbyteStreamStatus]) -> bool:
    return (len(status_messages) == 3 and status_messages[0] == AirbyteStreamStatus.STARTED
            and status_messages[1] == AirbyteStreamStatus.RUNNING and status_messages[2] == AirbyteStreamStatus.COMPLETE)


def validate_message_order(expected_message_order: List[Type], messages: List[AirbyteMessage]):
    if len(expected_message_order) != len(messages):
        pytest.fail(f"Expected message order count {len(expected_message_order)} did not match actual messages {len(messages)}")

    for i, message in enumerate(messages):
        if message.type != expected_message_order[i]:
            pytest.fail(f"At index {i} actual message type {message.type.name} did not match expected message type {expected_message_order[i].name}")
