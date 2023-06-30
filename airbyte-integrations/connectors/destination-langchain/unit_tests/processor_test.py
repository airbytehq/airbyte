#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import unittest.mock as mock
from typing import List, Tuple
from destination_langchain.processor import Processor
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
    return Processor(config=config, catalog=catalog)


def test_process_single_chunk_with_metadata_and_natural_ids():
    processor = initialize_processor()

    record = mock.MagicMock()
    record.stream = "stream1"
    record.data = {
        "id": 1,
        "text": "This is the text",
    }

    chunks, chunk_ids, ids_to_delete = processor.process(record)

    # Assert single chunk
    assert len(chunks) == 1

    # Assert chunk IDs
    assert len(chunk_ids) == 1

    # Assert IDs to delete (should be empty in this case)
    assert len(ids_to_delete) == 0


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

    chunks, chunk_ids, ids_to_delete = processor.process(record)

    # Assert multiple chunks
    assert len(chunks) == 2

    # Assert chunk IDs
    assert len(chunk_ids) == len(chunks)

    for chunk in chunks:
        assert chunk.metadata["age"] == 25
    # Assert IDs to delete (should be empty in this case)
    assert len(ids_to_delete) == 0


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

    chunks, chunk_ids, ids_to_delete = processor.process(record)

    # Assert single chunk
    assert len(chunks) > 1

    # Assert chunk IDs
    assert len(chunk_ids) == len(chunks)
    assert chunk_ids[0] == "99_0"  # Natural ID + chunk count
    assert chunk_ids[1] == "99_1"  # Natural ID + chunk count

    # Assert IDs to delete (should contain the natural ID)
    assert len(ids_to_delete) == 1
    assert ids_to_delete[0] == 99
