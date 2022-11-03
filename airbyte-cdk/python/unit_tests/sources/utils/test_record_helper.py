#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.utils.record_helper import data_to_airbyte_record


@pytest.mark.parametrize(
    "test_name, data, schema, expected_data",
    [("test_data_to_airbyte_record", {"id": 0, "field_A": 1.0, "field_B": "airbyte"}, {}, {"id": 0, "field_A": 1.0, "field_B": "airbyte"})],
)
def test_data_to_airbyte_record(test_name, data, schema, expected_data):
    NOW = 1234567
    stream_name = "my_stream"
    transformer = MagicMock()
    message = data_to_airbyte_record(stream_name, data, transformer, schema)
    message.record.emitted_at = NOW

    expected_message = AirbyteMessage(type=MessageType.RECORD, record=AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=NOW))

    transformer.transform.assert_called_with(data, schema)
    assert expected_message == message
