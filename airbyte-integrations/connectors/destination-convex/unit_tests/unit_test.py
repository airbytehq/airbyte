#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import io
import json
import logging
from typing import Any, Dict

import pytest
import responses
from destination_convex.client import ConvexClient
from destination_convex.config import ConvexConfig
from destination_convex.destination import DestinationConvex
from destination_convex.writer import ConvexWriter

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteMessageSerializer,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteCatalogSerializer,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)


DEDUP_TABLE_NAME = "dedup_stream"
DEDUP_INDEX_FIELD = "int_col"


@pytest.fixture(name="config")
def config_fixture() -> ConvexConfig:
    return {
        "deployment_url": "http://deployment_url.convex.cloud",
        "access_key": "abcdef01236789",
    }


@pytest.fixture(name="client")
def client_fixture(config) -> ConvexClient:
    return ConvexClient(config)


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {"string_col": {"type": "str"}, DEDUP_INDEX_FIELD: {"type": "integer"}}}

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="append_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="overwrite_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    dedup_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name=DEDUP_TABLE_NAME,
            json_schema=stream_schema,
            supported_sync_modes=[SyncMode.incremental],
        ),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append_dedup,
        primary_key=[[DEDUP_INDEX_FIELD]],
    )

    return ConfiguredAirbyteCatalog(streams=[append_stream, overwrite_stream, dedup_stream])


def state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def record(stream: str, str_value: str, int_value: int) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(stream=stream, data={"str_col": str_value, DEDUP_INDEX_FIELD: int_value}, emitted_at=0),
    )


def setup_good_responses(config):
    responses.add(responses.PUT, f"{config['deployment_url']}/api/streaming_import/clear_tables", status=200)
    responses.add(responses.POST, f"{config['deployment_url']}/api/streaming_import/import_airbyte_records", status=200)
    responses.add(responses.GET, f"{config['deployment_url']}/version", status=200)
    responses.add(responses.PUT, f"{config['deployment_url']}/api/streaming_import/add_primary_key_indexes", status=200)
    responses.add(
        responses.GET,
        f"{config['deployment_url']}/api/streaming_import/primary_key_indexes_ready",
        status=200,
        json={"indexesReady": True},
    )


def setup_bad_response(config):
    responses.add(
        responses.PUT,
        f"{config['deployment_url']}/api/streaming_import/clear_tables",
        status=400,
        body="error message",
    )


@responses.activate
def test_bad_write(config: ConvexConfig, configured_catalog: ConfiguredAirbyteCatalog):
    setup_bad_response(config)
    client = ConvexClient(config, {})
    with pytest.raises(Exception) as e:
        client.delete([])

    assert (
        "Request to `http://deployment_url.convex.cloud/api/streaming_import/clear_tables` failed with status code 400: error message"
        in str(e.value)
    )


@responses.activate
def test_check(config: ConvexConfig):
    setup_good_responses(config)
    destination = DestinationConvex()
    logger = logging.getLogger("airbyte")
    destination.check(logger, config)


@responses.activate
def test_write(config: ConvexConfig, configured_catalog: ConfiguredAirbyteCatalog):
    setup_good_responses(config)
    append_stream, overwrite_stream, dedup_stream = (
        configured_catalog.streams[0].stream.name,
        configured_catalog.streams[1].stream.name,
        configured_catalog.streams[2].stream.name,
    )

    first_state_message = state({"state": "1"})
    first_append_chunk = [record(append_stream, str(i), i) for i in range(5)]
    first_overwrite_chunk = [record(overwrite_stream, str(i), i) for i in range(5)]
    first_dedup_chunk = [record(dedup_stream, str(i), i) for i in range(10)]
    first_record_chunk = first_append_chunk + first_overwrite_chunk + first_dedup_chunk
    destination = DestinationConvex()
    output_state = list(
        destination.write(
            config,
            configured_catalog,
            [
                *first_record_chunk,
                first_state_message,
            ],
        )
    )[0]
    assert first_state_message == output_state

    second_state_message = state({"state": "2"})
    second_append_chunk = [record(append_stream, str(i), i) for i in range(5, 10)]
    second_overwrite_chunk = [record(overwrite_stream, str(i), i) for i in range(5, 10)]
    second_dedup_chunk = [record(dedup_stream, str(i + 2), i) for i in range(5)]
    second_record_chunk = second_append_chunk + second_overwrite_chunk + second_dedup_chunk
    output_state = list(
        destination.write(
            config,
            configured_catalog,
            [
                *second_record_chunk,
                second_state_message,
            ],
        )
    )[0]
    assert second_state_message == output_state


@pytest.mark.parametrize("namespace", [None, "public"])
@responses.activate
def test_table_setup_uses_record_namespace(config, configured_catalog, namespace):
    setup_good_responses(config)
    messages = []
    for stream in configured_catalog.streams:
        stream.stream.namespace = namespace
        message = record(stream.stream.name, "value", 1)
        message.record.namespace = namespace
        messages.append(message)

    list(DestinationConvex().write(config, configured_catalog, messages))

    prefix = f"{namespace}_" if namespace else ""
    bodies = {call.request.url.rsplit("/", 1)[-1]: json.loads(call.request.body) for call in responses.calls}
    assert bodies["clear_tables"] == {"tableNames": [f"{prefix}overwrite_stream"]}
    assert bodies["add_primary_key_indexes"] == {"indexes": {f"{prefix}{DEDUP_TABLE_NAME}": [[DEDUP_INDEX_FIELD]]}}
    assert bodies["primary_key_indexes_ready"] == {"tables": [f"{prefix}{DEDUP_TABLE_NAME}"]}
    batch = bodies["import_airbyte_records"]
    assert set(batch["tables"]) == {message["tableName"] for message in batch["messages"]}
    assert set(batch["tables"]) == {f"{prefix}{stream.stream.name}" for stream in configured_catalog.streams}


@pytest.mark.parametrize(
    "checkpoint",
    [
        {"data": {"cursor": 1}},
        {"type": "LEGACY", "data": {"cursor": 2}},
        {"type": "STREAM", "stream": {"stream_descriptor": {"name": "append_stream"}, "stream_state": {"cursor": 3}}},
        {"type": "GLOBAL", "global": {"shared_state": {"cursor": 4}, "stream_states": []}},
    ],
)
@pytest.mark.parametrize("fail_write", [False, True])
@responses.activate
def test_cli_preserves_checkpoints_only_after_successful_flush(
    config, configured_catalog, checkpoint, fail_write, tmp_path, monkeypatch, capsys
):
    setup_good_responses(config)
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(ConfiguredAirbyteCatalogSerializer.dump(configured_catalog)))
    checkpoint_messages = [{"type": "STATE", "state": {**checkpoint, "id": i, "future_metadata": {"keep": True}}} for i in range(2)]
    checkpoint_messages.append({"type": "STATE", "state": checkpoint})
    record_message = AirbyteMessageSerializer.dump(record("append_stream", "value", 1))
    input_bytes = "\n".join(json.dumps(message) for message in [record_message, *checkpoint_messages]).encode()
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(input_bytes)))

    def write_callback(request):
        assert not [json.loads(line) for line in capsys.readouterr().out.splitlines() if json.loads(line).get("type") == "STATE"]
        assert json.loads(request.body)["messages"][0]["data"][DEDUP_INDEX_FIELD] == 1
        return (500 if fail_write else 200, {}, "")

    responses.remove(responses.POST, f"{config['deployment_url']}/api/streaming_import/import_airbyte_records")
    responses.add_callback(
        responses.POST, f"{config['deployment_url']}/api/streaming_import/import_airbyte_records", callback=write_callback
    )
    responses.add(responses.POST, f"{config['deployment_url']}/api/streaming_import/import_airbyte_records", status=200)

    args = ["write", "--config", str(config_path), "--catalog", str(catalog_path)]
    if fail_write:
        with pytest.raises(Exception, match="status code 500"):
            DestinationConvex().run(args)
    else:
        DestinationConvex().run(args)
    output_states = [json.loads(line) for line in capsys.readouterr().out.splitlines() if json.loads(line).get("type") == "STATE"]
    assert output_states == ([] if fail_write else checkpoint_messages)


def test_writer_buffers_are_independent(config):
    first = ConvexWriter(ConvexClient(config, {}))
    second = ConvexWriter(ConvexClient(config, {}))
    first.queue_write_operation({"tableName": "items", "data": {"id": 1}})
    assert len(first.write_buffer) == 1
    assert second.write_buffer == []
