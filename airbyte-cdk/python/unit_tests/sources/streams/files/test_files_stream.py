#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import random
from datetime import datetime
from typing import Any, Dict, List, Mapping
from unittest.mock import MagicMock, patch

import pendulum
import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.files import FileInfo, IncrementalFilesStream, StorageFile
from airbyte_cdk.sources.streams.files.formats import CsvParser

from .formats.abstract_parser_tests import create_by_local_file, memory_limit

LOGGER = logging.getLogger("airbyte")


def mock_big_size_object():
    mock = MagicMock()
    mock.__sizeof__.return_value = 1000000001
    return mock


@pytest.fixture(name="five_file_infos")
def file_info_fixture():
    lst = []
    for x in range(5):
        rand_int = random.randint(0, 1556417921769)
        lst.append(FileInfo(f"dummyfile_{rand_int}", 10, pendulum.now() - pendulum.duration(milliseconds=rand_int)))
    return lst


# patching abstractmethods to empty set so we can instantiate ABC to test
@patch("airbyte_cdk.sources.streams.files.IncrementalFilesStream.__abstractmethods__", set())
class TestIncrementalFilesStream:
    @pytest.mark.parametrize(  # set return_schema to None for an expected fail
        "schema_string, return_schema",
        [
            (
                '{"id": "integer", "name": "string", "valid": "boolean", "code": "integer", "degrees": "number", "birthday": '
                '"string", "last_seen": "string"}',
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
        stream = IncrementalFilesStream(dataset="foo", provider={}, format={}, path_pattern="**")
        if return_schema is not None:
            assert str(stream._parse_user_input_schema(schema_string)) == str(return_schema)
        else:
            with pytest.raises(Exception) as e_info:
                stream._parse_user_input_schema(schema_string)
                LOGGER.debug(str(e_info))

    def test_name_property(self):
        dataset = "foo"
        stream = IncrementalFilesStream(dataset=dataset, provider={}, format={}, path_pattern="**")
        assert stream.name == dataset

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
    def test_match_target_schema(
        self, target_columns: List[str], record: Dict[str, Any], expected_return_record: Mapping[str, Any]
    ) -> None:
        fs = IncrementalFilesStream(dataset="dummy", provider={}, format={}, path_pattern="")
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
    @memory_limit(512)
    def test_add_extra_fields_from_map(
        self, extra_map: Mapping[str, Any], record: Dict[str, Any], expected_return_record: Mapping[str, Any]
    ) -> None:
        fs = IncrementalFilesStream(dataset="dummy", provider={}, format={}, path_pattern="")
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
    @memory_limit(512)
    def test_pattern_matched_file_iterator(self, patterns: str, filepaths: List[str], expected_filepaths: List[str]) -> None:
        fs = IncrementalFilesStream(dataset="dummy", provider={}, format={}, path_pattern=patterns)
        file_infos = [create_by_local_file(filepath) for filepath in filepaths]
        assert set([p.key for p in fs.pattern_matched_file_iterator(file_infos)]) == set(expected_filepaths)

    def test_get_time_ordered_file_infos(self, five_file_infos):
        stream = IncrementalFilesStream(dataset="foo", provider={}, format={}, path_pattern="**")
        with patch.object(stream, "file_iterator", MagicMock(return_value=five_file_infos)):
            lst = stream.get_time_ordered_file_infos()
        assert lst[0].last_modified < lst[1].last_modified < lst[2].last_modified < lst[3].last_modified < lst[4].last_modified

    @pytest.mark.parametrize(
        "latest_record, current_stream_state, expected",
        [
            (  # overwrite history file
                {"id": 1, "_ab_source_file_last_modified": "2022-05-11T11:54:11+0000", "_ab_source_file_url": "new_test_file.csv"},
                {"_ab_source_file_last_modified": "2021-07-25T15:33:04+0000", "history": {"2021-07-25": {"old_test_file.csv"}}},
                {"2022-05-11": {"new_test_file.csv"}},
            ),
            (  # add file to same day
                {"id": 1, "_ab_source_file_last_modified": "2022-07-25T11:54:11+0000", "_ab_source_file_url": "new_test_file.csv"},
                {"_ab_source_file_last_modified": "2022-07-25T00:00:00+0000", "history": {"2022-07-25": {"old_test_file.csv"}}},
                {"2022-07-25": {"new_test_file.csv", "old_test_file.csv"}},
            ),
            (  # add new day to history
                {"id": 1, "_ab_source_file_last_modified": "2022-07-03T11:54:11+0000", "_ab_source_file_url": "new_test_file.csv"},
                {"_ab_source_file_last_modified": "2022-07-01T00:00:00+0000", "history": {"2022-07-01": {"old_test_file.csv"}}},
                {"2022-07-01": {"old_test_file.csv"}, "2022-07-03": {"new_test_file.csv"}},
            ),
            (  # history size limit reached
                {"_ab_source_file_url": "test.csv"},
                {"_ab_source_file_last_modified": "2022-07-01T00:00:00+0000", "history": mock_big_size_object()},
                None,
            ),
        ],
        ids=["overwrite_history_file", "add_file_to_same_day ", "add_new_day_to_history", "history_size_limit_reached"],
    )
    def test_get_updated_history(self, latest_record, current_stream_state, expected, request) -> None:
        fs = IncrementalFilesStream(dataset="dummy", provider={}, format={"filetype": "csv"}, path_pattern="**/prefix*.csv")
        fs._get_schema_map = MagicMock(return_value={})
        assert fs.get_updated_state(current_stream_state, latest_record).get("history") == expected

        if request.node.callspec.id == "history_size_limit_reached":
            assert fs.sync_all_files_always

    @pytest.mark.parametrize(  # set expected_return_record to None for an expected fail
        "stream_state, expected_error",
        [
            (None, False),
            ({"_ab_source_file_last_modified": "2021-07-25T15:33:04+0000"}, False),
            ({"_ab_source_file_last_modified": "2021-07-25T15:33:04Z"}, False),
            ({"_ab_source_file_last_modified": "2021-07-25"}, True),
        ],
    )
    def test_get_datetime_from_stream_state(self, stream_state, expected_error):
        if not expected_error:
            assert isinstance(
                IncrementalFilesStream(
                    dataset="dummy", provider={"bucket": "test-test"}, format={}, path_pattern="**/prefix*.csv"
                )._get_datetime_from_stream_state(stream_state=stream_state),
                datetime,
            )
        else:
            with pytest.raises(Exception):
                assert isinstance(
                    IncrementalFilesStream(
                        dataset="dummy", provider={"bucket": "test-test"}, format={}, path_pattern="**/prefix*.csv"
                    )._get_datetime_from_stream_state(stream_state=stream_state),
                    datetime,
                )

    def test_fileformatparser_class_exception(self):
        stream = IncrementalFilesStream(dataset="foo", provider={}, format={"filetype": "NON-EXISTENT_format"}, path_pattern="**")
        with pytest.raises(RuntimeError) as e_info:
            stream.fileformatparser_class
            LOGGER.debug(str(e_info))

    @pytest.mark.parametrize(
        "stream_kwargs, mock_inferred_schema, expected_schema_columns",
        [
            (  # basic test
                {"dataset": "foo", "provider": {}, "format": {"filetype": "csv"}, "path_pattern": "**"},
                {"col_a": "string", "col_b": "integer"},
                {"col_a": "string", "col_b": "integer"},
            ),
            (  # provided schema
                {
                    "dataset": "foo",
                    "provider": {},
                    "format": {"filetype": "csv"},
                    "path_pattern": "**",
                    "schema": '{"col_a": "string", "col_b":"integer"}',
                },
                {"col_a": "string", "col_b": "integer"},
                {"col_a": "string", "col_b": "integer"},
            ),
        ],
    )
    @patch("airbyte_cdk.sources.streams.files.IncrementalFilesStream.storagefile_class", StorageFile)
    @patch("airbyte_cdk.sources.streams.files.StorageFile.__abstractmethods__", set())
    def test_get_json_schema(self, stream_kwargs, mock_inferred_schema, expected_schema_columns, five_file_infos):
        expected_schema = {
            "properties": {
                IncrementalFilesStream.ab_additional_col: {"type": "object"},
                IncrementalFilesStream.ab_last_mod_col: {"format": "date-time", "type": "string"},
                IncrementalFilesStream.ab_file_name_col: {"type": "string"},
            },
            "type": "object",
        }
        for col, typ in expected_schema_columns.items():
            expected_schema["properties"][col] = {"type": ["null", typ]}

        stream = IncrementalFilesStream(**stream_kwargs)
        with patch.object(stream, "file_iterator", MagicMock(return_value=five_file_infos)):
            with patch.object(stream.storagefile_class, "open", MagicMock()):
                with patch.object(CsvParser, "get_inferred_schema", MagicMock(return_value=mock_inferred_schema)):
                    schema = stream.get_json_schema()
                    assert schema == expected_schema

    @pytest.mark.parametrize(
        "sync_mode, state_date",
        [
            (SyncMode.full_refresh, None),
            (SyncMode.incremental, None),
            (SyncMode.incremental, pendulum.now() - pendulum.duration(years=25)),
        ],
    )
    @patch("airbyte_cdk.sources.streams.files.IncrementalFilesStream.storagefile_class", StorageFile)
    @patch("airbyte_cdk.sources.streams.files.StorageFile.__abstractmethods__", set())
    def test_stream_slices(self, sync_mode, state_date, five_file_infos):

        stream = IncrementalFilesStream(dataset="foo", provider={}, format={}, path_pattern="**")
        # get unique datetimes from the five_file_infos, extemely likely to be 5 but just to be robust
        unique_dates = list(set([inf.last_modified for inf in five_file_infos]))
        stream_state = None
        if state_date:
            stream_state = {stream.cursor_field: datetime.strftime(state_date, stream.datetime_format_string)}
            # get number of datetimes after stream state if we have it
            unique_dates = [d for d in unique_dates if d > state_date]
        num_unique_dates = len(unique_dates)

        with patch.object(stream, "file_iterator", MagicMock(return_value=five_file_infos)):
            slices = stream.stream_slices(sync_mode, stream.cursor_field, stream_state)
            slice_list = [s for s in slices]
        LOGGER.info(f"number of slices: {len(slice_list)}")
        assert len(slice_list) == num_unique_dates
