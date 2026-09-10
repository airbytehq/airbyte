# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import pytest
from destination_duckdb.destination import DestinationDuckdb, validated_sql_name
from orjson import orjson

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteGlobalState,
    AirbyteMessage,
    AirbyteMessageSerializer,
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteCatalogSerializer,
    ConnectorSpecification,
    Status,
    StreamDescriptor,
    Type,
)


class StateDestination(Destination):
    def check(self, logger, config):
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def spec(self, logger):
        return ConnectorSpecification(connectionSpecification={})

    def write(self, config, configured_catalog, input_messages):
        yield from input_messages


def test_read_invalid_path():
    invalid_input = "/test.duckdb"
    with pytest.raises(ValueError):
        _ = DestinationDuckdb._get_destination_path(invalid_input)

    assert True


@pytest.mark.parametrize(
    "input, expected",
    [
        ("test", "test"),
        ("test_123", "test_123"),
        ("test;123", None),
        ("test123;", None),
        ("test-123", None),
        ("test 123", None),
        ("test.123", None),
        ("test,123", None),
        ("test!123", None),
    ],
)
def test_validated_sql_name(input, expected):
    if expected is None:
        with pytest.raises(ValueError):
            validated_sql_name(input)
    else:
        assert validated_sql_name(input) == expected


def test_destination_run_serializes_global_state_with_protocol_alias(tmp_path, monkeypatch, capsys):
    message = AirbyteMessage(
        type=Type.STATE,
        state=AirbyteStateMessage(
            type=AirbyteStateType.GLOBAL,
            global_=AirbyteGlobalState(
                shared_state=AirbyteStateBlob({"cdc_state": "ok"}),
                stream_states=[
                    AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="customers", namespace="public"),
                        stream_state=AirbyteStateBlob({"cursor": "1"}),
                    )
                ],
            ),
        ),
    )
    config_path = tmp_path / "config.json"
    catalog_path = tmp_path / "catalog.json"
    messages_path = tmp_path / "messages.jsonl"
    config_path.write_text("{}", encoding="utf-8")
    catalog_path.write_text(
        orjson.dumps(ConfiguredAirbyteCatalogSerializer.dump(ConfiguredAirbyteCatalog(streams=[]))).decode(), encoding="utf-8"
    )
    messages_path.write_text(orjson.dumps(AirbyteMessageSerializer.dump(message)).decode() + "\n", encoding="utf-8")

    with messages_path.open(encoding="utf-8") as input_messages:
        monkeypatch.setattr("sys.stdin", input_messages)
        StateDestination().run(["write", "--config", str(config_path), "--catalog", str(catalog_path)])

    output_lines = [line for line in capsys.readouterr().out.splitlines() if '"type":"STATE"' in line]
    assert len(output_lines) == 1
    serialized_message = orjson.loads(output_lines[0])
    serialized_state = serialized_message["state"]

    assert serialized_state["type"] == "GLOBAL"
    assert "global" in serialized_state
    assert "global_" not in serialized_state
    assert orjson.dumps(serialized_message).decode() == (
        '{"type":"STATE","state":{"type":"GLOBAL","global":{"stream_states":'
        '[{"stream_descriptor":{"name":"customers","namespace":"public"},"stream_state":{"cursor":"1"}}],'
        '"shared_state":{"cdc_state":"ok"}}}}'
    )
