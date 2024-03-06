#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.destinations.vector_db_based.config import (
    CodeSplitterConfigModel,
    FieldNameMappingConfigModel,
    MarkdownHeaderSplitterConfigModel,
    ProcessingConfigModel,
    SeparatorSplitterConfigModel,
)
from airbyte_cdk.destinations.vector_db_based.document_processor import DocumentProcessor
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream
from airbyte_cdk.models.airbyte_protocol import AirbyteRecordMessage, DestinationSyncMode, SyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


def initialize_processor(config=ProcessingConfigModel(chunk_size=48, chunk_overlap=0, text_fields=None, metadata_fields=None)):
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="stream1",
                    json_schema={},
                    namespace="namespace1",
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
                primary_key=[["id"]],
            ),
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="stream2",
                    json_schema={},
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            ),
        ]
    )
    return DocumentProcessor(config=config, catalog=catalog)


@pytest.mark.parametrize(
    "metadata_fields, expected_metadata",
    [
        (
            None,
            {
                "_ab_stream": "namespace1_stream1",
                "id": 1,
                "text": "This is the text",
                "complex": {"test": "abc"},
                "arr": [{"test": "abc"}, {"test": "def"}],
            },
        ),
        (["id"], {"_ab_stream": "namespace1_stream1", "id": 1}),
        (["id", "non_existing"], {"_ab_stream": "namespace1_stream1", "id": 1}),
        (
            ["id", "complex.test"],
            {"_ab_stream": "namespace1_stream1", "id": 1, "complex.test": "abc"},
        ),
        (
            ["id", "arr.*.test"],
            {"_ab_stream": "namespace1_stream1", "id": 1, "arr.*.test": ["abc", "def"]},
        ),
    ],
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


def test_process_single_chunk_limited_metadata():
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
                stream=AirbyteStream(
                    name="stream1",
                    json_schema={},
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
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
            "other_nested": {"non_text": {"a": "xyz", "b": "abc"}},
        },
        emitted_at=1234,
    )

    processor.text_fields = [
        "nested.texts.*.text",
        "text",
        "other_nested.non_text",
        "non.*.existing",
    ]
    processor.metadata_fields = ["non_text", "non_text_2", "id"]

    chunks, _ = processor.process(record)

    assert len(chunks) == 1
    assert (
        chunks[0].page_content
        == """nested.texts.*.text: This is the text
And another
text: This is the regular text
other_nested.non_text: \na: xyz
b: abc"""
    )
    assert chunks[0].metadata == {
        "id": 1,
        "non_text": "a",
        "non_text_2": 1,
        "_ab_stream": "namespace1_stream1",
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
    "label, text, chunk_size, chunk_overlap, splitter_config, expected_chunks",
    [
        (
            "Default splitting",
            "By default, splits are done \non multi newlines,\n\n then single newlines, then spaces",
            10,
            0,
            None,
            [
                "text: By default, splits are done",
                "on multi newlines,",
                "then single newlines, then spaces",
            ],
        ),
        (
            "Overlap splitting",
            "One two three four five six seven eight nine ten eleven twelve thirteen",
            15,
            5,
            None,
            [
                "text: One two three four five six",
                "four five six seven eight nine ten",
                "eight nine ten eleven twelve thirteen",
            ],
        ),
        (
            "Special tokens",
            "Special tokens like <|endoftext|> are treated like regular text",
            15,
            0,
            None,
            [
                "text: Special tokens like",
                "<|endoftext|> are treated like regular",
                "text",
            ],
        ),
        (
            "Custom separator",
            "Custom \nseparatorxxxDoes not split on \n\nnewlines",
            10,
            0,
            SeparatorSplitterConfigModel(mode="separator", separators=['"xxx"']),
            [
                "text: Custom \nseparator",
                "Does not split on \n\nnewlines\n",
            ],
        ),
        (
            "Only splits if chunks dont fit",
            "Does yyynot usexxxseparators yyyif not needed",
            10,
            0,
            SeparatorSplitterConfigModel(mode="separator", separators=['"xxx"', '"yyy"']),
            [
                "text: Does yyynot use",
                "separators yyyif not needed",
            ],
        ),
        (
            "Use first separator first",
            "Does alwaysyyy usexxxmain separators yyyfirst",
            10,
            0,
            SeparatorSplitterConfigModel(mode="separator", separators=['"yyy"', '"xxx"']),
            [
                "text: Does always",
                "usexxxmain separators yyyfirst",
            ],
        ),
        (
            "Basic markdown splitting",
            "# Heading 1\nText 1\n\n# Heading 2\nText 2\n\n# Heading 3\nText 3",
            10,
            0,
            MarkdownHeaderSplitterConfigModel(mode="markdown", split_level=1),
            [
                "text: # Heading 1\nText 1\n",
                "# Heading 2\nText 2",
                "# Heading 3\nText 3",
            ],
        ),
        (
            "Split multiple levels",
            "# Heading 1\nText 1\n\n## Sub-Heading 1\nText 2\n\n# Heading 2\nText 3",
            10,
            0,
            MarkdownHeaderSplitterConfigModel(mode="markdown", split_level=2),
            [
                "text: # Heading 1\nText 1\n",
                "\n## Sub-Heading 1\nText 2\n",
                "# Heading 2\nText 3",
            ],
        ),
        (
            "Do not split if split level does not allow",
            "## Heading 1\nText 1\n\n## Heading 2\nText 2\n\n## Heading 3\nText 3",
            10,
            0,
            MarkdownHeaderSplitterConfigModel(mode="markdown", split_level=1),
            [
                "text: ## Heading 1\nText 1\n\n## Heading 2\nText 2\n\n## Heading 3\nText 3\n",
            ],
        ),
        (
            "Do not split if everything fits",
            "## Does not split if everything fits. Heading 1\nText 1\n\n## Heading 2\nText 2\n\n## Heading 3\nText 3",
            1000,
            0,
            MarkdownHeaderSplitterConfigModel(mode="markdown", split_level=5),
            [
                "text: ## Does not split if everything fits. Heading 1\nText 1\n\n## Heading 2\nText 2\n\n## Heading 3\nText 3",
            ],
        ),
        (
            "Split Java code, respecting class boundaries",
            "class A { /* \n\nthis is the first class */ }\nclass B {}",
            20,
            0,
            CodeSplitterConfigModel(mode="code", language="java"),
            [
                "text: class A { /* \n\nthis is the first class */ }",
                "class B {}",
            ],
        ),
        (
            "Split Java code as proto, not respecting class boundaries",
            "class A { /* \n\nthis is the first class */ }\nclass B {}",
            20,
            0,
            CodeSplitterConfigModel(mode="code", language="proto"),
            [
                "text: class A { /*",
                "this is the first class */ }\nclass B {}",
            ],
        ),
    ],
)
def test_text_splitters(label, text, chunk_size, chunk_overlap, splitter_config, expected_chunks):
    processor = initialize_processor(
        ProcessingConfigModel(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            text_fields=["text"],
            metadata_fields=None,
            text_splitter=splitter_config,
        )
    )

    record = AirbyteRecordMessage(
        stream="stream1",
        namespace="namespace1",
        data={
            "id": 1,
            "name": "John Doe",
            "text": text,
            "age": 25,
        },
        emitted_at=1234,
    )

    processor.text_fields = ["text"]

    chunks, id_to_delete = processor.process(record)

    assert len(chunks) == len(expected_chunks)

    # check that the page_content in each chunk equals the expected chunk
    for i, chunk in enumerate(chunks):
        print(chunk.page_content)
        assert chunk.page_content == expected_chunks[i]
    assert id_to_delete is None


@pytest.mark.parametrize(
    "label, split_config, has_error_message",
    [
        (
            "Invalid separator",
            SeparatorSplitterConfigModel(mode="separator", separators=['"xxx']),
            True,
        ),
        (
            "Missing quotes",
            SeparatorSplitterConfigModel(mode="separator", separators=["xxx"]),
            True,
        ),
        (
            "Non-string separator",
            SeparatorSplitterConfigModel(mode="separator", separators=["123"]),
            True,
        ),
        (
            "Object separator",
            SeparatorSplitterConfigModel(mode="separator", separators=["{}"]),
            True,
        ),
        (
            "Proper separator",
            SeparatorSplitterConfigModel(mode="separator", separators=['"xxx"', '"\\n\\n"']),
            False,
        ),
    ],
)
def test_text_splitter_check(label, split_config, has_error_message):
    error = DocumentProcessor.check_config(
        ProcessingConfigModel(
            chunk_size=48,
            chunk_overlap=0,
            text_fields=None,
            metadata_fields=None,
            text_splitter=split_config,
        )
    )
    if has_error_message:
        assert error is not None
    else:
        assert error is None


@pytest.mark.parametrize(
    "mappings, fields, expected_chunk_metadata",
    [
        (None, {"abc": "def", "xyz": 123}, {"abc": "def", "xyz": 123}),
        ([], {"abc": "def", "xyz": 123}, {"abc": "def", "xyz": 123}),
        (
            [FieldNameMappingConfigModel(from_field="abc", to_field="AAA")],
            {"abc": "def", "xyz": 123},
            {"AAA": "def", "xyz": 123},
        ),
        (
            [FieldNameMappingConfigModel(from_field="non_existing", to_field="AAA")],
            {"abc": "def", "xyz": 123},
            {"abc": "def", "xyz": 123},
        ),
    ],
)
def test_rename_metadata_fields(
    mappings: Optional[List[FieldNameMappingConfigModel]],
    fields: Mapping[str, Any],
    expected_chunk_metadata: Mapping[str, Any],
):
    processor = initialize_processor()

    record = AirbyteRecordMessage(
        stream="stream1",
        namespace="namespace1",
        data={**fields, "text": "abc"},
        emitted_at=1234,
    )

    processor.field_name_mappings = mappings
    processor.text_fields = ["text"]

    chunks, id_to_delete = processor.process(record)

    assert len(chunks) == 1
    assert chunks[0].metadata == {
        **expected_chunk_metadata,
        "_ab_stream": "namespace1_stream1",
        "text": "abc",
    }


@pytest.mark.parametrize(
    "primary_key_value, stringified_primary_key, primary_key",
    [
        ({"id": 99}, "namespace1_stream1_99", [["id"]]),
        (
            {"id": 99, "name": "John Doe"},
            "namespace1_stream1_99_John Doe",
            [["id"], ["name"]],
        ),
        (
            {"id": 99, "name": "John Doe", "age": 25},
            "namespace1_stream1_99_John Doe_25",
            [["id"], ["name"], ["age"]],
        ),
        (
            {"nested": {"id": "abc"}, "name": "John Doe"},
            "namespace1_stream1_abc_John Doe",
            [["nested", "id"], ["name"]],
        ),
        (
            {"nested": {"id": "abc"}},
            "namespace1_stream1_abc___not_found__",
            [["nested", "id"], ["name"]],
        ),
    ],
)
def test_process_multiple_chunks_with_dedupe_mode(
    primary_key_value: Mapping[str, Any],
    stringified_primary_key: str,
    primary_key: List[List[str]],
):
    processor = initialize_processor()

    record = AirbyteRecordMessage(
        stream="stream1",
        namespace="namespace1",
        data={
            "text": "This is the text and it is long enough to be split into multiple chunks. This is the text and it is long enough to be split into multiple chunks. This is the text and it is long enough to be split into multiple chunks",
            "age": 25,
            **primary_key_value,
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


@pytest.mark.parametrize(
    "record, sync_mode, has_chunks, raises, expected_id_to_delete",
    [
        pytest.param(
            AirbyteRecordMessage(
                stream="stream1",
                namespace="namespace1",
                data={"text": "This is the text", "id": "1"},
                emitted_at=1234,
            ),
            DestinationSyncMode.append_dedup,
            True,
            False,
            "namespace1_stream1_1",
            id="update",
        ),
        pytest.param(
            AirbyteRecordMessage(
                stream="stream1",
                namespace="namespace1",
                data={"text": "This is the text", "id": "1"},
                emitted_at=1234,
            ),
            DestinationSyncMode.append,
            True,
            False,
            None,
            id="append",
        ),
        pytest.param(
            AirbyteRecordMessage(
                stream="stream1",
                namespace="namespace1",
                data={"text": "This is the text", "id": "1", "_ab_cdc_deleted_at": 1234},
                emitted_at=1234,
            ),
            DestinationSyncMode.append_dedup,
            False,
            False,
            "namespace1_stream1_1",
            id="cdc_delete",
        ),
        pytest.param(
            AirbyteRecordMessage(
                stream="stream1",
                namespace="namespace1",
                data={"id": "1", "_ab_cdc_deleted_at": 1234},
                emitted_at=1234,
            ),
            DestinationSyncMode.append_dedup,
            False,
            False,
            "namespace1_stream1_1",
            id="cdc_delete_without_text",
        ),
        pytest.param(
            AirbyteRecordMessage(
                stream="stream1",
                namespace="namespace1",
                data={"id": "1"},
                emitted_at=1234,
            ),
            DestinationSyncMode.append_dedup,
            False,
            True,
            "namespace1_stream1_1",
            id="update_without_text",
        ),
    ],
)
def test_process_cdc_records(record, sync_mode, has_chunks, raises, expected_id_to_delete):
    processor = initialize_processor()

    processor.text_fields = ["text"]

    processor.streams["namespace1_stream1"].destination_sync_mode = sync_mode

    if raises:
        with pytest.raises(AirbyteTracedException):
            processor.process(record)
    else:
        chunks, id_to_delete = processor.process(record)
        if has_chunks:
            assert len(chunks) > 0
        assert id_to_delete == expected_id_to_delete
