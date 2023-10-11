#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, mock_open, patch

import pytest
from source_s3.v4.unstructured_parser import UnstructuredParser
from unstructured.documents.elements import CheckBox, Formula, ListItem, Text, Title
from unstructured.file_utils.filetype import FileType


@pytest.mark.asyncio
async def test_infer_schema():
    schema = await UnstructuredParser().infer_schema(MagicMock(), MagicMock(), MagicMock(), MagicMock())
    assert schema == {
            "content": {"type": "string"},
            "chunk_number": {"type": "integer"},
            "no_of_chunks": {"type": "integer"},
            "id": {"type": "string"},
        }

@pytest.mark.parametrize(
    "filetype, parse_result, expected_records",
    [
        pytest.param(
            FileType.MD,
            "test",
            [
                {
                    "content": "test",
                    "chunk_number": 0,
                    "no_of_chunks": 1,
                    "id": "path/to/file.xyz_0",
                }
            ],
            id="markdown file",
        ),
        pytest.param(
            FileType.CSV,
            "test",
            [],
            id="wrong file format",
        ),
        pytest.param(
            FileType.PDF,
            [
                Title("heading"),
                Text("This is the text"),
                ListItem("This is a list item"),
                Formula("This is a formula"),
            ],
            [
                {
                    "content": "# heading\n\nThis is the text\n\n- This is a list item\n\n```\nThis is a formula\n```",
                    "chunk_number": 0,
                    "no_of_chunks": 1,
                    "id": "path/to/file.xyz_0",
                }
            ],
            id="pdf file",
        ),
        pytest.param(
            FileType.DOCX,
            [
                Title("heading"),
                Text("This is the text"),
                ListItem("This is a list item"),
                Formula("This is a formula"),
            ],
            [
                {
                    "content": "# heading\n\nThis is the text\n\n- This is a list item\n\n```\nThis is a formula\n```",
                    "chunk_number": 0,
                    "no_of_chunks": 1,
                    "id": "path/to/file.xyz_0",
                }
            ],
            id="docx file",
        ),
        pytest.param(
            FileType.MD,
            "a"*4_000_005,
            [
                {
                    "content": "a"*4_000_000,
                    "chunk_number": 0,
                    "no_of_chunks": 2,
                    "id": "path/to/file.xyz_0",
                },
                {
                    "content": "a"*5,
                    "chunk_number": 1,
                    "no_of_chunks": 2,
                    "id": "path/to/file.xyz_1",
                }
            ],
            id="multi-chunk markdown",
        ),
        pytest.param(
            FileType.PDF,
            [Text("a"*4_000_005)],
            [
                {
                    "content": "a"*4_000_000,
                    "chunk_number": 0,
                    "no_of_chunks": 2,
                    "id": "path/to/file.xyz_0",
                },
                {
                    "content": "a"*5,
                    "chunk_number": 1,
                    "no_of_chunks": 2,
                    "id": "path/to/file.xyz_1",
                }
            ],
            id="multi-chunk markdown",
        ),
    ]
)
@patch("unstructured.partition.auto.partition")
@patch("unstructured.partition.md.optional_decode")
@patch("unstructured.file_utils.filetype.detect_filetype")
def test_parse_records(mock_detect_filetype, mock_optional_decode, mock_partition, filetype, parse_result, expected_records):
    file_uri = "path/to/file.xyz"
    stream_reader = MagicMock()
    mock_open(stream_reader.open_file, read_data=str(parse_result))
    fake_file = MagicMock()
    fake_file.uri = file_uri
    logger = MagicMock()
    mock_detect_filetype.return_value = filetype
    mock_partition.return_value = parse_result
    mock_optional_decode.side_effect = lambda x: x
    assert list(UnstructuredParser().parse_records(MagicMock(), fake_file, stream_reader, logger, MagicMock())) == expected_records