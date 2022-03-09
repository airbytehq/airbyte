#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, List, Mapping
from unittest.mock import patch

import pytest
from airbyte_cdk import AirbyteLogger
from source_s3.source_files_abstract.stream import FileStream

from .abstract_test_parser import create_by_local_file, memory_limit

LOGGER = AirbyteLogger()


class TestFileStream:
    @pytest.mark.parametrize(  # set return_schema to None for an expected fail
        "schema_string, return_schema",
        [
            (
                '{"id": "integer", "name": "string", "valid": "boolean", "code": "integer", "degrees": "number", "birthday": "string", "last_seen": "string"}',
                {
                    "id": "integer",
                    "name": "string",
                    "valid": "boolean",
                    "code": "integer",
                    "degrees": "number",
                    "birthday": "string",
                    "last_seen": "string",
                },
            ),
            ('{"single_column": "boolean"}', {"single_column": "boolean"}),
            (r"{}", {}),
            ('{this isn\'t right: "integer"}', None),  # invalid json
            ('[ {"a":"b"} ]', None),  # array instead of object
            ('{"a": "boolean", "b": {"string": "integer"}}', None),  # object as a value
            ('{"a": ["boolean", "string"], "b": {"string": "integer"}}', None),  # array and object as values
            ('{"a": "integer", "b": "NOT A REAL DATATYPE"}', None),  # incorrect datatype
            ('{"a": "NOT A REAL DATATYPE", "b": "ANOTHER FAKE DATATYPE"}', None),  # multiple incorrect datatypes
        ],
    )
    @memory_limit(512)
    def test_parse_user_input_schema(self, schema_string: str, return_schema: str) -> None:
        if return_schema is not None:
            assert str(FileStream._parse_user_input_schema(schema_string)) == str(return_schema)
        else:
            with pytest.raises(Exception) as e_info:
                FileStream._parse_user_input_schema(schema_string)
                LOGGER.debug(str(e_info))

    @pytest.mark.parametrize(  # set expected_return_record to None for an expected fail
        "target_columns, record, expected_return_record",
        [
            (  # simple case
                ["id", "first_name", "last_name"],
                {"id": "1", "first_name": "Frodo", "last_name": "Baggins"},
                {"id": "1", "first_name": "Frodo", "last_name": "Baggins", "_ab_additional_properties": {}},
            ),
            (  # additional columns
                ["id", "first_name", "last_name"],
                {"id": "1", "first_name": "Frodo", "last_name": "Baggins", "location": "The Shire", "items": ["The One Ring", "Sting"]},
                {
                    "id": "1",
                    "first_name": "Frodo",
                    "last_name": "Baggins",
                    "_ab_additional_properties": {"location": "The Shire", "items": ["The One Ring", "Sting"]},
                },
            ),
            (  # missing columns
                ["id", "first_name", "last_name", "location", "items"],
                {"id": "1", "first_name": "Frodo", "last_name": "Baggins"},
                {
                    "id": "1",
                    "first_name": "Frodo",
                    "last_name": "Baggins",
                    "location": None,
                    "items": None,
                    "_ab_additional_properties": {},
                },
            ),
            (  # additional and missing columns
                ["id", "first_name", "last_name", "friends", "enemies"],
                {"id": "1", "first_name": "Frodo", "last_name": "Baggins", "location": "The Shire", "items": ["The One Ring", "Sting"]},
                {
                    "id": "1",
                    "first_name": "Frodo",
                    "last_name": "Baggins",
                    "friends": None,
                    "enemies": None,
                    "_ab_additional_properties": {"location": "The Shire", "items": ["The One Ring", "Sting"]},
                },
            ),
        ],
        ids=["simple_case", "additional_columns", "missing_columns", "additional_and_missing_columns"],
    )
    @patch(
        "source_s3.source_files_abstract.stream.FileStream.__abstractmethods__", set()
    )  # patching abstractmethods to empty set so we can instantiate ABC to test
    def test_match_target_schema(
        self, target_columns: List[str], record: Dict[str, Any], expected_return_record: Mapping[str, Any]
    ) -> None:
        fs = FileStream(dataset="dummy", provider={}, format={}, path_pattern="")
        if expected_return_record is not None:
            assert fs._match_target_schema(record, target_columns) == expected_return_record
        else:
            with pytest.raises(Exception) as e_info:
                fs._match_target_schema(record, target_columns)
                LOGGER.debug(str(e_info))

    @pytest.mark.parametrize(  # set expected_return_record to None for an expected fail
        "extra_map, record, expected_return_record",
        [
            (  # one extra field
                {"friend": "Frodo"},
                {"id": "1", "first_name": "Samwise", "last_name": "Gamgee"},
                {"id": "1", "first_name": "Samwise", "last_name": "Gamgee", "friend": "Frodo"},
            ),
            (  # multiple extra fields
                {"friend": "Frodo", "enemy": "Gollum", "loves": "PO-TAY-TOES"},
                {"id": "1", "first_name": "Samwise", "last_name": "Gamgee"},
                {"id": "1", "first_name": "Samwise", "last_name": "Gamgee", "friend": "Frodo", "enemy": "Gollum", "loves": "PO-TAY-TOES"},
            ),
            (  # empty extra_map
                {},
                {"id": "1", "first_name": "Samwise", "last_name": "Gamgee"},
                {"id": "1", "first_name": "Samwise", "last_name": "Gamgee"},
            ),
        ],
        ids=["one_extra_field", "multiple_extra_fields", "empty_extra_map"],
    )
    @patch(
        "source_s3.source_files_abstract.stream.FileStream.__abstractmethods__", set()
    )  # patching abstractmethods to empty set so we can instantiate ABC to test
    @memory_limit(512)
    def test_add_extra_fields_from_map(
        self, extra_map: Mapping[str, Any], record: Dict[str, Any], expected_return_record: Mapping[str, Any]
    ) -> None:
        fs = FileStream(dataset="dummy", provider={}, format={}, path_pattern="")
        if expected_return_record is not None:
            assert fs._add_extra_fields_from_map(record, extra_map) == expected_return_record
        else:
            with pytest.raises(Exception) as e_info:
                fs._add_extra_fields_from_map(record, extra_map)
                LOGGER.debug(str(e_info))

    @pytest.mark.parametrize(
        "patterns, filepaths, expected_filepaths",
        [
            (  # 'everything' case
                "**",
                [
                    "file.csv",
                    "file.parquet",
                    "folder/file.csv",
                    "folder/file.parquet",
                    "folder/nested/file.csv",
                    "folder/nested/file.parquet",
                    "a/b/c/d/e/f/file",
                ],
                [
                    "file.csv",
                    "file.parquet",
                    "folder/file.csv",
                    "folder/file.parquet",
                    "folder/nested/file.csv",
                    "folder/nested/file.parquet",
                    "a/b/c/d/e/f/file",
                ],
            ),
            (  # specific filetype only
                "**/*.csv",
                [
                    "file.csv",
                    "file.parquet",
                    "folder/file.csv",
                    "folder/file.parquet",
                    "folder/nested/file.csv",
                    "folder/nested/file.parquet",
                    "a/b/c/d/e/f/file",
                ],
                ["file.csv", "folder/file.csv", "folder/nested/file.csv"],
            ),
            (  # specific filetypes only
                "**/*.csv|**/*.parquet",
                [
                    "file.csv",
                    "file.parquet",
                    "folder/file.csv",
                    "folder/file.parquet",
                    "folder/nested/file.csv",
                    "folder/nested/file.parquet",
                    "a/b/c/d/e/f/file",
                ],
                [
                    "file.csv",
                    "file.parquet",
                    "folder/file.csv",
                    "folder/file.parquet",
                    "folder/nested/file.csv",
                    "folder/nested/file.parquet",
                ],
            ),
            (  # 'everything' only 1 level deep
                "*/*",
                [
                    "file.csv",
                    "file.parquet",
                    "folder/file.csv",
                    "folder/file.parquet",
                    "folder/nested/file.csv",
                    "folder/nested/file.parquet",
                    "a/b/c/d/e/f/file",
                ],
                ["folder/file.csv", "folder/file.parquet"],
            ),
            (  # 'everything' at least 1 level deep
                "*/**",
                [
                    "file.csv",
                    "file.parquet",
                    "folder/file.csv",
                    "folder/file.parquet",
                    "folder/nested/file.csv",
                    "folder/nested/file.parquet",
                    "a/b/c/d/e/f/file",
                ],
                ["folder/file.csv", "folder/file.parquet", "folder/nested/file.csv", "folder/nested/file.parquet", "a/b/c/d/e/f/file"],
            ),
            (  # 'everything' at least 3 levels deep
                "*/*/*/**",
                [
                    "file.csv",
                    "file.parquet",
                    "folder/file.csv",
                    "folder/file.parquet",
                    "folder/nested/file.csv",
                    "folder/nested/file.parquet",
                    "a/b/c/d/e/f/file",
                ],
                ["a/b/c/d/e/f/file"],
            ),
            (  # specific filetype at least 1 level deep
                "*/**/*.csv",
                [
                    "file.csv",
                    "file.parquet",
                    "folder/file.csv",
                    "folder/file.parquet",
                    "folder/nested/file.csv",
                    "folder/nested/file.parquet",
                    "a/b/c/d/e/f/file",
                ],
                ["folder/file.csv", "folder/nested/file.csv"],
            ),
            (  # 'everything' with specific filename (any filetype)
                "**/file.*|**/file",
                [
                    "NOT_THIS_file.csv",
                    "folder/NOT_THIS_file.csv",
                    "file.csv",
                    "file.parquet",
                    "folder/file.csv",
                    "folder/file.parquet",
                    "folder/nested/file.csv",
                    "folder/nested/file.parquet",
                    "a/b/c/d/e/f/file",
                ],
                [
                    "file.csv",
                    "file.parquet",
                    "folder/file.csv",
                    "folder/file.parquet",
                    "folder/nested/file.csv",
                    "folder/nested/file.parquet",
                    "a/b/c/d/e/f/file",
                ],
            ),
            (  # specific dir / any dir / specific dir / any file
                "folder/*/files/*",
                [
                    "file.csv",
                    "folder/file.csv",
                    "wrongfolder/xyz/files/1",
                    "a/b/c/d/e/f/file",
                    "folder/abc/files/1",
                    "folder/abc/logs/1",
                    "folder/xyz/files/1",
                ],
                ["folder/abc/files/1", "folder/xyz/files/1"],
            ),
            (  # specific file prefix and filetype, anywhere
                "**/prefix*.csv",
                [
                    "file.csv",
                    "prefix-file.parquet",
                    "prefix-file.csv",
                    "folder/file.parquet",
                    "folder/nested/prefixmylovelyfile.csv",
                    "folder/nested/prefix-file.parquet",
                ],
                ["prefix-file.csv", "folder/nested/prefixmylovelyfile.csv"],
            ),
        ],
        ids=[
            "everything case",
            "specific filetype only",
            "specific filetypes only",
            "everything only 1 level deep",
            "everything at least 1 level deep",
            "everything at least 3 levels deep",
            "specific filetype at least 1 level deep",
            "everything with specific filename (any filetype)",
            "specific dir / any dir / specific dir / any file",
            "specific file prefix and filetype, anywhere",
        ],
    )
    @patch(
        "source_s3.source_files_abstract.stream.FileStream.__abstractmethods__", set()
    )  # patching abstractmethods to empty set so we can instantiate ABC to test
    @memory_limit(512)
    def test_pattern_matched_filepath_iterator(self, patterns: str, filepaths: List[str], expected_filepaths: List[str]) -> None:
        fs = FileStream(dataset="dummy", provider={}, format={}, path_pattern=patterns)
        file_infos = [create_by_local_file(filepath) for filepath in filepaths]
        assert set([p.key for p in fs.pattern_matched_filepath_iterator(file_infos)]) == set(expected_filepaths)
