#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream
from airbyte_cdk.models.airbyte_protocol import AirbyteRecordMessage, DestinationSyncMode, SyncMode
from destination_langchain.config import ProcessingConfigModel
from destination_langchain.document_processor import DocumentProcessor


def initialize_processor():
    config = ProcessingConfigModel(chunk_size=48, chunk_overlap=0, text_fields=None)
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="stream1", json_schema={}, namespace="namespace1", supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
                primary_key=[["id"]],
            ),
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="stream2", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            ),
        ]
    )
    return DocumentProcessor(config=config, catalog=catalog)


def test_process_single_chunk_without_metadata():
    processor = initialize_processor()

    record = AirbyteRecordMessage(
        stream="stream1",
        namespace="namespace1",
        data={
            "id": 1,
            "text": "This is the text",
        },
        emitted_at=1234,
    )

    chunks, id_to_delete = processor.process(record)

    assert len(chunks) == 1
    # natural id is only set for dedup mode
    assert "_record_id" not in chunks[0].metadata
    assert chunks[0].metadata["_airbyte_stream"] == "namespace1_stream1"
    assert chunks[0].page_content == "id: 1\ntext: This is the text"
    assert id_to_delete is None


def test_process_single_chunk_without_namespace():
    config = ProcessingConfigModel(chunk_size=48, chunk_overlap=0, text_fields=None)
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="stream1", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            ),
        ]
    )
    processor = DocumentProcessor(config=config, catalog=catalog)

    record = AirbyteRecordMessage(
        stream="stream1",
        data={
            "id": 1,
            "text": "This is the text",
        },
        emitted_at=1234,
    )

    chunks, _ = processor.process(record)
    assert chunks[0].metadata["_airbyte_stream"] == "stream1"


def test_complex_text_fields():
    processor = initialize_processor()

    record = AirbyteRecordMessage(
        stream="stream1",
        namespace="namespace1",
        data={
            "id": 1,
            "nested": {
                "texts": [
                    {"text": "This is the text"},
                    {"text": "And another"},
                ]
            },
            "non_text": "a",
            "non_text_2": 1,
            "text": "This is the regular text",
            "other_nested": {
                "non_text": {
                    "a": "xyz",
                    "b": "abc"
                }
            }
        },
        emitted_at=1234,
    )

    processor.text_fields = ["nested.texts.*.text", "text", "other_nested.non_text", "non.*.existing"]

    chunks, _ = processor.process(record)

    assert len(chunks) == 1
    assert chunks[0].page_content == """nested.texts.*.text: This is the text
And another
text: This is the regular text
other_nested.non_text: \na: xyz
b: abc"""
    assert chunks[0].metadata == {
        "id": 1,
        "non_text": "a",
        "non_text_2": 1,
        "_airbyte_stream": "namespace1_stream1"
    }


def test_non_text_fields():
    processor = initialize_processor()

    record = AirbyteRecordMessage(
        stream="stream1",
        namespace="namespace1",
        data={
            "id": 1,
            "text": "This is the regular text",
        },
        emitted_at=1234,
    )

    processor.text_fields = ["another_field"]
    processor.logger = MagicMock()

    chunks, id_to_delete = processor.process(record)

    assert len(chunks) == 0
    assert id_to_delete is None
    assert processor.logger.warning.called


def test_metadata_normalization():
    processor = initialize_processor()

    record = AirbyteRecordMessage(
        stream="stream1",
        namespace="namespace1",
        data={
            "id": 1,
            "a_complex_field": {"a_nested_field": "a_nested_value"},
            "too_big": "a" * 1000,
            "small": "a",
            "text": "This is the text",
        },
        emitted_at=1234,
    )

    processor.text_fields = ["text"]
    processor.max_metadata_size = 100

    chunks, id_to_delete = processor.process(record)

    assert len(chunks) == 1
    assert chunks[0].page_content == "text: This is the text"
    assert id_to_delete is None

    for chunk in chunks:
        assert len(chunk.metadata) == 3
        assert "a_complex_field" not in chunk.metadata
        assert "too_big" not in chunk.metadata
        assert "small" in chunk.metadata


def test_process_multiple_chunks_with_relevant_fields():
    processor = initialize_processor()

    record = AirbyteRecordMessage(
        stream="stream1",
        namespace="namespace1",
        data={
            "id": 1,
            "name": "John Doe",
            "text": "This is the text and it is long enough to be split into multiple chunks. This is the text and it is long enough to be split into multiple chunks. This is the text and it is long enough to be split into multiple chunks",
            "age": 25,
        },
        emitted_at=1234,
    )

    processor.text_fields = ["text"]

    chunks, id_to_delete = processor.process(record)

    assert len(chunks) == 2

    for chunk in chunks:
        assert chunk.metadata["age"] == 25
    assert id_to_delete is None


def test_process_multiple_chunks_with_dedupe_mode():
    processor = initialize_processor()

    record = AirbyteRecordMessage(
        stream="stream1",
        namespace="namespace1",
        data={
            "id": 99,
            "text": "This is the text and it is long enough to be split into multiple chunks. This is the text and it is long enough to be split into multiple chunks. This is the text and it is long enough to be split into multiple chunks",
            "age": 25,
        },
        emitted_at=1234,
    )

    processor.text_fields = ["text"]

    processor.streams["namespace1_stream1"].destination_sync_mode = DestinationSyncMode.append_dedup
    processor.streams["namespace1_stream1"].primary_key = [["id"]]  # Primary key defined

    chunks, id_to_delete = processor.process(record)

    assert len(chunks) > 1
    assert chunks[0].metadata["_record_id"] == 99
    assert id_to_delete == 99
