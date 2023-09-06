#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.destinations.vector_db_based.config import ProcessingConfigModel
from airbyte_cdk.destinations.vector_db_based.document_processor import DocumentProcessor
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream
from airbyte_cdk.models.airbyte_protocol import AirbyteRecordMessage, DestinationSyncMode, SyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


def initialize_processor():
    config = ProcessingConfigModel(chunk_size=48, chunk_overlap=0, text_fields=None, metadata_fields=None)
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


@pytest.mark.parametrize(
    "metadata_fields, expected_metadata",
    [
        (None, {"_ab_stream": "namespace1_stream1", "id": 1, "text": "This is the text", "complex": {"test": "abc"}, "arr": [{"test": "abc"}, {"test": "def"}]}),
        (["id"], {"_ab_stream": "namespace1_stream1", "id": 1}),
        (["id", "non_existing"], {"_ab_stream": "namespace1_stream1", "id": 1}),
        (["id", "complex.test"], {"_ab_stream": "namespace1_stream1", "id": 1, "complex.test": "abc"}),
        (["id", "arr.*.test"], {"_ab_stream": "namespace1_stream1", "id": 1, "arr.*.test": ["abc", "def"]}),
    ]
)
def test_process_single_chunk_with_metadata(metadata_fields, expected_metadata):
    processor = initialize_processor()
    processor.metadata_fields = metadata_fields

    record = AirbyteRecordMessage(
        stream="stream1",
        namespace="namespace1",
        data={
            "id": 1,
            "text": "This is the text",
            "complex": {"test": "abc"},
            "arr": [{"test": "abc"}, {"test": "def"}],
        },
        emitted_at=1234,
    )

    chunks, id_to_delete = processor.process(record)

    assert len(chunks) == 1
    # natural id is only set for dedup mode
    assert "_ab_record_id" not in chunks[0].metadata
    assert chunks[0].metadata == expected_metadata
    assert id_to_delete is None


def test_process_single_chunk_limit4ed_metadata():
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
    assert "_ab_record_id" not in chunks[0].metadata
    assert chunks[0].metadata["_ab_stream"] == "namespace1_stream1"
    assert chunks[0].metadata["id"] == 1
    assert chunks[0].metadata["text"] == "This is the text"
    assert chunks[0].page_content == "id: 1\ntext: This is the text"
    assert id_to_delete is None


def test_process_single_chunk_without_namespace():
    config = ProcessingConfigModel(chunk_size=48, chunk_overlap=0, text_fields=None, metadata_fields=None)
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
    assert chunks[0].metadata["_ab_stream"] == "stream1"


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
    processor.metadata_fields = ["non_text", "non_text_2", "id"]

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
        "_ab_stream": "namespace1_stream1"
    }


def test_no_text_fields():
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

    # assert process is throwing with no text fields found
    with pytest.raises(AirbyteTracedException):
        processor.process(record)


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


@pytest.mark.parametrize(
    "primary_key_value, stringified_primary_key, primary_key",
    [
        ({"id": 99}, "namespace1_stream1_99", [["id"]]),
        ({"id": 99, "name": "John Doe"}, "namespace1_stream1_99_John Doe", [["id"], ["name"]]),
        ({"id": 99, "name": "John Doe", "age": 25}, "namespace1_stream1_99_John Doe_25", [["id"], ["name"], ["age"]]),
        ({"nested": {"id": "abc"}, "name": "John Doe"}, "namespace1_stream1_abc_John Doe", [["nested", "id"], ["name"]]),
        ({"nested": {"id": "abc"}}, "namespace1_stream1_abc___not_found__", [["nested", "id"], ["name"]]),
    ]
)
def test_process_multiple_chunks_with_dedupe_mode(primary_key_value: Mapping[str, Any], stringified_primary_key: str, primary_key: List[List[str]]):
    processor = initialize_processor()

    record = AirbyteRecordMessage(
        stream="stream1",
        namespace="namespace1",
        data={
            "text": "This is the text and it is long enough to be split into multiple chunks. This is the text and it is long enough to be split into multiple chunks. This is the text and it is long enough to be split into multiple chunks",
            "age": 25,
            **primary_key_value
        },
        emitted_at=1234,
    )

    processor.text_fields = ["text"]

    processor.streams["namespace1_stream1"].destination_sync_mode = DestinationSyncMode.append_dedup
    processor.streams["namespace1_stream1"].primary_key = primary_key

    chunks, id_to_delete = processor.process(record)

    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.metadata["_ab_record_id"] == stringified_primary_key
    assert id_to_delete == stringified_primary_key
