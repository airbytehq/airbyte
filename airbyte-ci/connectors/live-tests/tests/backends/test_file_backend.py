# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
from airbyte_protocol.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    ConnectorSpecification,
    Status,
)
from airbyte_protocol.models import Type as AirbyteMessageType

from live_tests.commons.backends import FileBackend


@pytest.mark.parametrize(
    "messages, expected_writes",
    [
        (
            [
                AirbyteMessage(type=AirbyteMessageType.CATALOG, catalog=AirbyteCatalog(streams=[])),
                AirbyteMessage(
                    type=AirbyteMessageType.CONNECTION_STATUS,
                    connectionStatus=AirbyteConnectionStatus(status=Status.SUCCEEDED),
                ),
                AirbyteMessage(
                    type=AirbyteMessageType.RECORD,
                    record=AirbyteRecordMessage(stream="test_stream", data={}, emitted_at=123456789),
                ),
                AirbyteMessage(
                    type=AirbyteMessageType.SPEC,
                    spec=ConnectorSpecification(connectionSpecification={}),
                ),
                AirbyteMessage(
                    type=AirbyteMessageType.STATE,
                    state=AirbyteStateMessage(data={"test": "value"}),
                ),
            ],
            [
                ("catalog.jsonl", '{"streams": []}\n'),
                (
                    "connection_status.jsonl",
                    '{"status": "SUCCEEDED", "message": null}\n',
                ),
                (
                    "records.jsonl",
                    '{"namespace": null, "stream": "test_stream", "data": {}, "meta": null}\n',
                ),
                (
                    "spec.jsonl",
                    '{"documentationUrl": null, "changelogUrl": null, "connectionSpecification": {}, "supportsIncremental": null, "supportsNormalization": false, "supportsDBT": false, "supported_destination_sync_modes": null, "advanced_auth": null, "protocol_version": null}\n',
                ),
                (
                    "states.jsonl",
                    '{"type": null, "stream": null, "global_": null, "data": {"test": "value"}, "sourceStats": null, "destinationStats": null}\n',
                ),
            ],
        ),
    ],
)
def test_write(tmp_path, messages, expected_writes):
    backend = FileBackend(tmp_path)
    backend.write(messages)
    for expected_file, expected_content in expected_writes:
        expected_path = Path(tmp_path / expected_file)
        assert expected_path.exists()
        content = expected_path.read_text()
