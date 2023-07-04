#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import unittest.mock as mock
from typing import List, Tuple
from destination_langchain.document_processor import DocumentProcessor
from destination_langchain.config import ProcessingConfigModel
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode, SyncMode


def initialize_processor():
    config = ProcessingConfigModel(chunk_size=48, chunk_overlap=0, text_fields=None)
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="stream1", json_schema={}),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
                primary_key=[["id"]],
            ),
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="stream2", json_schema={}),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            ),
        ]
    )
    return DocumentProcessor(config=config, catalog=catalog)


def test_process_single_chunk_with_metadata_and_natural_ids():
    processor = initialize_processor()

    record = mock.MagicMock()
    record.stream = "stream1"
    record.data = {
        "id": 1,
        "text": "This is the text",
    }

    chunks, id_to_delete = processor.process(record)

    # Assert single chunk
    assert len(chunks) == 1

    # Assert IDs to delete (should be empty in this case)
    assert id_to_delete is None

def test_metadat_normalization():
    processor = initialize_processor()

    record = mock.MagicMock()
    record.stream = "stream1"
    record.data = {
        "id": 1,
        "a_complex_field": {
            "a_nested_field": "a_nested_value"
        },
        "too_big": "a" * 1000,
        "small": "a",
        "text": "This is the text",
    }

    processor.text_fields = ["text"]
    processor.max_metadata_size = 100

    chunks, id_to_delete = processor.process(record)

    # Assert single chunk
    assert len(chunks) == 1

    for chunk in chunks:
        assert len(chunk.metadata) == 3
        assert "a_complex_field" not in chunk.metadata
        assert "too_big" not in chunk.metadata
        assert "small" in chunk.metadata


def test_process_multiple_chunks_with_relevant_fields():
    processor = initialize_processor()

    record = mock.MagicMock()
    record.stream = "stream1"
    record.data = {
        "id": 1,
        "name": "John Doe",
        "text": "This is the text and it is long enough to be split into multiple chunks. This is the text and it is long enough to be split into multiple chunks. This is the text and it is long enough to be split into multiple chunks",
        "age": 25,
    }

    processor.text_fields = ["text"]

    chunks, id_to_delete = processor.process(record)

    # Assert multiple chunks
    assert len(chunks) == 2

    for chunk in chunks:
        assert chunk.metadata["age"] == 25
    # Assert IDs to delete (should be empty in this case)
    assert id_to_delete is None


def test_process_multiple_chunks_with_dedupe_mode():
    processor = initialize_processor()

    record = mock.MagicMock()
    record.stream = "stream1"
    record.data = {
        "id": 99,
        "text": "This is the text and it is long enough to be split into multiple chunks. This is the text and it is long enough to be split into multiple chunks. This is the text and it is long enough to be split into multiple chunks",
        "age": 25,
    }

    processor.text_fields = ["text"]

    processor.streams["stream1"].destination_sync_mode = DestinationSyncMode.append_dedup
    processor.streams["stream1"].primary_key = [["id"]]  # Primary key defined

    chunks, id_to_delete = processor.process(record)

    # Assert single chunk
    assert len(chunks) > 1

    # Assert IDs to delete (should contain the natural ID)
    assert id_to_delete == 99
