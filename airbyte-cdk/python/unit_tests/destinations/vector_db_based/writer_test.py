#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional
from unittest.mock import ANY, MagicMock, call

import pytest
from airbyte_cdk.destinations.vector_db_based import ProcessingConfigModel, Writer
from airbyte_cdk.models import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteCatalogSerializer,
    Level,
    Type,
)


def _generate_record_message(index: int, stream: str = "example_stream", namespace: Optional[str] = None):
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=stream, namespace=namespace, emitted_at=1234, data={"column_name": f"value {index}", "id": index}
        ),
    )


BATCH_SIZE = 32


def generate_stream(name: str = "example_stream", namespace: Optional[str] = None):
    return {
        "stream": {
            "name": name,
            "namespace": namespace,
            "json_schema": {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {}},
            "supported_sync_modes": ["full_refresh", "incremental"],
            "source_defined_cursor": False,
            "default_cursor_field": ["column_name"],
        },
        "primary_key": [["id"]],
        "sync_mode": "incremental",
        "destination_sync_mode": "append_dedup",
    }


def generate_mock_embedder():
    mock_embedder = MagicMock()
    mock_embedder.embed_documents.return_value = [[0] * 1536] * (BATCH_SIZE + 5 + 5)
    mock_embedder.embed_documents.side_effect = lambda chunks: [[0] * 1536] * len(chunks)

    return mock_embedder


@pytest.mark.parametrize("omit_raw_text", [True, False])
def test_write(omit_raw_text: bool):
    """
    Basic test for the write method, batcher and document processor.
    """
    config_model = ProcessingConfigModel(chunk_overlap=0, chunk_size=1000, metadata_fields=None, text_fields=["column_name"])

    configured_catalog: ConfiguredAirbyteCatalog = ConfiguredAirbyteCatalogSerializer.load({"streams": [generate_stream()]})
    # messages are flushed after 32 records or after a state message, so this will trigger two batches to be processed
    input_messages = [_generate_record_message(i) for i in range(BATCH_SIZE + 5)]
    state_message = AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage())
    input_messages.append(state_message)
    # messages are also flushed once the input messages are exhausted, so this will trigger another batch
    input_messages.extend([_generate_record_message(i) for i in range(5)])

    mock_embedder = generate_mock_embedder()

    mock_indexer = MagicMock()
    post_sync_log_message = AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="post sync"))
    mock_indexer.post_sync.return_value = [post_sync_log_message]

    # Create the DestinationLangchain instance
    writer = Writer(config_model, mock_indexer, mock_embedder, BATCH_SIZE, omit_raw_text)

    output_messages = writer.write(configured_catalog, input_messages)
    output_message = next(output_messages)
    # assert state message is
    assert output_message == state_message

    mock_indexer.pre_sync.assert_called_with(configured_catalog)

    # 1 batches due to max batch size reached and 1 batch due to state message
    assert mock_indexer.index.call_count == 2
    assert mock_indexer.delete.call_count == 2
    assert mock_embedder.embed_documents.call_count == 2

    if omit_raw_text:
        for call_args in mock_indexer.index.call_args_list:
            for chunk in call_args[0][0]:
                if omit_raw_text:
                    assert chunk.page_content is None
                else:
                    assert chunk.page_content is not None

    output_message = next(output_messages)
    assert output_message == post_sync_log_message

    try:
        next(output_messages)
        assert False, "Expected end of message stream"
    except StopIteration:
        pass

    # 1 batch due to end of message stream
    assert mock_indexer.index.call_count == 3
    assert mock_indexer.delete.call_count == 3
    assert mock_embedder.embed_documents.call_count == 3

    mock_indexer.post_sync.assert_called()


def test_write_stream_namespace_split():
    """
    Test separate handling of streams and namespaces in the writer

    generate BATCH_SIZE - 10 records for example_stream, 5 records for example_stream with namespace abc and 10 records for example_stream2
    messages are flushed after 32 records or after a state message, so this will trigger 4 calls to the indexer:
    * out of the first batch of 32, example_stream, example stream with namespace abd and the first 5 records for example_stream2
    * in the second batch, the remaining 5 records for example_stream2
    """
    config_model = ProcessingConfigModel(chunk_overlap=0, chunk_size=1000, metadata_fields=None, text_fields=["column_name"])

    configured_catalog: ConfiguredAirbyteCatalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                generate_stream(),
                generate_stream(namespace="abc"),
                generate_stream("example_stream2"),
            ]
        }
    )

    input_messages = [_generate_record_message(i, "example_stream", None) for i in range(BATCH_SIZE - 10)]
    input_messages.extend([_generate_record_message(i, "example_stream", "abc") for i in range(5)])
    input_messages.extend([_generate_record_message(i, "example_stream2", None) for i in range(10)])
    state_message = AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage())
    input_messages.append(state_message)

    mock_embedder = generate_mock_embedder()

    mock_indexer = MagicMock()
    mock_indexer.post_sync.return_value = []

    # Create the DestinationLangchain instance
    writer = Writer(config_model, mock_indexer, mock_embedder, BATCH_SIZE, False)

    output_messages = writer.write(configured_catalog, input_messages)
    next(output_messages)

    mock_indexer.index.assert_has_calls(
        [
            call(ANY, None, "example_stream"),
            call(ANY, "abc", "example_stream"),
            call(ANY, None, "example_stream2"),
            call(ANY, None, "example_stream2"),
        ]
    )
    mock_indexer.index.assert_has_calls(
        [
            call(ANY, None, "example_stream"),
            call(ANY, "abc", "example_stream"),
            call(ANY, None, "example_stream2"),
            call(ANY, None, "example_stream2"),
        ]
    )
    assert mock_embedder.embed_documents.call_count == 4
