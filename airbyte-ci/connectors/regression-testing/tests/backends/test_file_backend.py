from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest
from airbyte_protocol.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStreamState,
    ConnectorSpecification,
    Level,
    Status,
    StreamDescriptor,
)
from airbyte_protocol.models import Type as AirbyteMessageType
from regression_testing.backends.file_backend import FileBackend


@pytest.mark.asyncio
@pytest.mark.parametrize("messages, expected_writes", [
    ([
        AirbyteMessage(type=AirbyteMessageType.CATALOG, catalog=AirbyteCatalog(streams=[])),
        AirbyteMessage(type=AirbyteMessageType.CONNECTION_STATUS, connectionStatus=AirbyteConnectionStatus(status=Status.SUCCEEDED)),
        AirbyteMessage(type=AirbyteMessageType.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={}, emitted_at=123456789)),
        AirbyteMessage(type=AirbyteMessageType.SPEC, spec=ConnectorSpecification(connectionSpecification={})),
        AirbyteMessage(type=AirbyteMessageType.STATE, state=AirbyteStateMessage(data={"test": "value"})),
    ],
    [
        ("catalog.jsonl", '{"streams": []}\n'),
        ("connection_status.jsonl", '{"status": "SUCCEEDED", "message": null}\n'),
        ("test_stream/records.jsonl", '{"namespace": null, "stream": "test_stream", "data": {}, "emitted_at": 123456789, "meta": null}\n'),
        ("spec.jsonl", '{"documentationUrl": null, "changelogUrl": null, "connectionSpecification": {}, "supportsIncremental": null, "supportsNormalization": false, "supportsDBT": false, "supported_destination_sync_modes": null, "advanced_auth": null, "protocol_version": null}\n'),
        ("_global_states/states.jsonl", '{"type": null, "stream": null, "global_": null, "data": {"test": "value"}, "sourceStats": null, "destinationStats": null}\n'),
    ]),
])
async def test_write(messages, expected_writes):
    output_directory = "fake-output-directory"

    m = mock_open()
    with patch("builtins.open", m), patch("os.makedirs") as mock_makedirs:
        backend = FileBackend(output_directory)
        await backend.write((msg for msg in messages))  # Use a generator

    for stream in {"test_stream"}:
        mock_makedirs.assert_any_call(f"{output_directory}/{stream}", exist_ok=True)

    for file_name, content in expected_writes:
        m.assert_any_call(f"{output_directory}/{file_name}", "w")
        m().write.assert_any_call(content)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message, expected",
    [
        pytest.param(
            AirbyteMessage(type=AirbyteMessageType.CATALOG, catalog=AirbyteCatalog(streams=[])),
            {"catalog": 1},
            id="catalog-is-in-messages-by-type",
        ),
        pytest.param(
            AirbyteMessage(type=AirbyteMessageType.CONNECTION_STATUS, connectionStatus=None),
            {"connection_status": 1},
            id="connection-status-is-in-messages-by-type",
        ),
        pytest.param(
            AirbyteMessage(type=AirbyteMessageType.RECORD, record=AirbyteRecordMessage(stream="test_stream", data={}, emitted_at=123456789)),
            {"records": {"test_stream": 1}},
            id="record-is-in-messages-by-type",
        ),
        pytest.param(
            AirbyteMessage(type=AirbyteMessageType.SPEC, spec=ConnectorSpecification(connectionSpecification={})),
            {"spec": 1},
            id="spec-is-in-messages-by-type",
        ),
        pytest.param(
            AirbyteMessage(type=AirbyteMessageType.STATE, state=AirbyteStateMessage(data={"test": "value"})),
            {"states": {"_global_states": 1}},
            id="state-without-stream-descriptor-is-in-messages-by-type",
        ),
        pytest.param(
            AirbyteMessage(
                type=AirbyteMessageType.STATE,
                state=AirbyteStateMessage(
                    data={"test": "value"},
                    stream=AirbyteStreamState(stream_descriptor=StreamDescriptor(name="test-name", namespace=None)))),
            {"states": {"test-name": 1}},
            id="state-with-stream-descriptor-and-no-namespace-is-in-messages-by-type",
        ),
        pytest.param(
            AirbyteMessage(
                type=AirbyteMessageType.STATE,
                state=AirbyteStateMessage(
                    data={"test": "value"},
                    stream=AirbyteStreamState(stream_descriptor=StreamDescriptor(name="test-name", namespace="test-namespace")))),
            {"states": {"test-name_test-namespace": 1}},
            id="state-with-stream-descriptor-and-namespace-is-in-messages-by-type",
        ),
        pytest.param(
            AirbyteMessage(type=AirbyteMessageType.LOG, log=AirbyteLogMessage(level=Level.WARN, message="")),
            None,
            id="log-is-not-in-messages-by-type",
        ),
        pytest.param("Not an AirbyteMessage", None, id="non-airbyte-message-is-ignored"),
    ],
)
def test_get_messages_by_type(message, expected):
    messages_by_type = FileBackend._get_messages_by_type((msg for msg in [message]))  # Single-item generator

    if expected is None:
        assert all(len(v) == 0 for v in messages_by_type.values() if isinstance(v, list))
        assert all(len(v) == 0 for v in messages_by_type["records"].values())
        assert all(len(v) == 0 for v in messages_by_type["states"].values())
    else:
        for key, value in expected.items():
            if isinstance(value, int):
                assert len(messages_by_type[key]) == value
            elif isinstance(value, dict):
                for subkey, subvalue in value.items():
                    assert len(messages_by_type[key][subkey]) == subvalue
