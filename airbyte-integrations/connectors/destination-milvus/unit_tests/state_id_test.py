#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import io
import logging
from unittest.mock import Mock, patch

import destination_milvus.destination as destination_module
import orjson
from destination_milvus.destination import DestinationMilvus

from airbyte_cdk.models import AirbyteMessageSerializer, Type


STREAM_STATE = {
    "type": "STATE",
    "state": {
        "type": "STREAM",
        "stream": {
            "stream_descriptor": {"name": "products"},
            "stream_state": {"updated_at": "2026-10-01"},
        },
        "id": 42,
    },
}

GLOBAL_STATE = {
    "type": "STATE",
    "state": {
        "type": "GLOBAL",
        "global": {
            "shared_state": {"updated_at": "2026-10-01"},
            "stream_states": [
                {
                    "stream_descriptor": {"name": "products"},
                    "stream_state": {"cursor": "2026-10-01"},
                }
            ],
        },
        "id": "abc",
    },
}


def _parse_message(message: dict):
    line = orjson.dumps(message).decode()
    return next(iter(DestinationMilvus()._parse_input_stream(io.StringIO(line))))


def _serialize_message(message):
    serializer = getattr(destination_module, "serialize_airbyte_message", AirbyteMessageSerializer.dump)
    return serializer(message)


def test_stream_state_id_round_trips():
    message = _parse_message(STREAM_STATE)

    serialized = _serialize_message(message)

    assert serialized["state"]["id"] == 42
    assert {key: value for key, value in serialized["state"].items() if key != "id"} == {
        key: value for key, value in STREAM_STATE["state"].items() if key != "id"
    }


def test_global_state_id_round_trips():
    message = _parse_message(GLOBAL_STATE)

    serialized = _serialize_message(message)

    assert serialized["state"]["id"] == "abc"
    assert serialized["state"]["global"] == GLOBAL_STATE["state"]["global"]


def test_full_write_path_preserves_state_id(tmp_path):
    config = {
        "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
        "embedding": {"mode": "openai", "openai_key": "mykey"},
        "indexing": {
            "host": "https://notmilvus.com",
            "collection": "test2",
            "auth": {"mode": "token", "token": "mytoken"},
            "vector_field": "vector",
            "text_field": "text",
        },
    }
    catalog = {
        "streams": [
            {
                "stream": {
                    "name": "products",
                    "json_schema": {
                        "type": "object",
                        "properties": {"str_col": {"type": "string"}},
                    },
                    "supported_sync_modes": ["full_refresh"],
                    "source_defined_cursor": False,
                    "default_cursor_field": [],
                },
                "sync_mode": "full_refresh",
                "destination_sync_mode": "append",
            }
        ]
    }
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_bytes(orjson.dumps(catalog))
    record = {
        "type": "RECORD",
        "record": {
            "stream": "products",
            "data": {"str_col": "A Milvus product"},
            "emitted_at": 1_791_302_400_000,
        },
    }
    input_stream = io.StringIO("\n".join((orjson.dumps(record).decode(), orjson.dumps(STREAM_STATE).decode())))

    embedder = Mock()
    embedder.embedding_dimensions = 2
    embedder.embed_documents.return_value = [[0.1, 0.2]]
    indexer = Mock()
    indexer.post_sync.return_value = []
    with (
        patch("destination_milvus.destination.MilvusIndexer", return_value=indexer),
        patch("destination_milvus.destination.create_from_config", return_value=embedder),
    ):
        outputs = list(
            DestinationMilvus()._run_write(
                config=config,
                configured_catalog_path=str(catalog_path),
                input_stream=input_stream,
            )
        )

    state = next(message for message in outputs if message.type == Type.STATE)
    assert _serialize_message(state)["state"]["id"] == 42
    embedder.embed_documents.assert_called_once()
    indexer.post_sync.assert_called_once()


def test_run_prints_state_id(capsys):
    message = _parse_message(STREAM_STATE)
    with (
        patch.object(DestinationMilvus, "parse_args", return_value=Mock()),
        patch.object(DestinationMilvus, "run_cmd", return_value=[message]),
    ):
        DestinationMilvus().run([])

    printed_lines = capsys.readouterr().out.splitlines()
    assert len(printed_lines) == 1
    assert orjson.loads(printed_lines[0])["state"]["id"] == 42


def test_state_without_extras_serializes_identically():
    state_without_extras = {
        "type": "STATE",
        "state": {
            "type": "STREAM",
            "stream": {
                "stream_descriptor": {"name": "products"},
                "stream_state": {"updated_at": "2026-10-01"},
            },
        },
    }
    message = _parse_message(state_without_extras)

    assert not hasattr(message.state, "_airbyte_additional_properties")
    assert _serialize_message(message) == AirbyteMessageSerializer.dump(message)


def test_record_messages_are_unaffected():
    record = {
        "type": "RECORD",
        "record": {
            "stream": "products",
            "data": {"str_col": "A Milvus product"},
            "emitted_at": 1_791_302_400_000,
        },
    }
    message = _parse_message(record)

    assert message.type == Type.RECORD
    assert _serialize_message(message) == AirbyteMessageSerializer.dump(message)


def test_invalid_json_line_is_skipped(caplog):
    record = {
        "type": "RECORD",
        "record": {
            "stream": "products",
            "data": {"str_col": "A Milvus product"},
            "emitted_at": 1_791_302_400_000,
        },
    }
    valid_line = orjson.dumps(record).decode()
    with caplog.at_level(logging.INFO, logger="airbyte"):
        messages = list(DestinationMilvus()._parse_input_stream(io.StringIO(f"not json\n{valid_line}")))

    assert len(messages) == 1
    assert messages[0].type == Type.RECORD
    assert "ignoring input which can't be deserialized as Airbyte Message: not json" in caplog.text
