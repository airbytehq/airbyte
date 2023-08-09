#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping
from unittest.mock import MagicMock, patch

import pytest
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from source_s3.source_files_abstract.file_info import FileInfo
from source_s3.source_files_abstract.storagefile import StorageFile
from source_s3.source_files_abstract.stream import IncrementalFileStream
from source_s3.stream import IncrementalFileStreamS3

from .abstract_test_parser import create_by_local_file, memory_limit

LOGGER = AirbyteLogger()


def mock_big_size_object():
    mock = MagicMock()
    mock.__sizeof__.return_value = 1000000001
    return mock


class TestIncrementalFileStream:
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
        if return_schema is not None:
            assert str(IncrementalFileStream._parse_user_input_schema(schema_string)) == str(return_schema)
        else:
            with pytest.raises(Exception) as e_info:
                IncrementalFileStream._parse_user_input_schema(schema_string)
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
        "source_s3.source_files_abstract.stream.IncrementalFileStream.__abstractmethods__", set()
    )  # patching abstractmethods to empty set so we can instantiate ABC to test
    @memory_limit(512)
    def test_add_extra_fields_from_map(
        self, extra_map: Mapping[str, Any], record: Dict[str, Any], expected_return_record: Mapping[str, Any]
    ) -> None:
        fs = IncrementalFileStream(dataset="dummy", provider={}, format={}, path_pattern="")
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
        "source_s3.source_files_abstract.stream.IncrementalFileStream.__abstractmethods__", set()
    )  # patching abstractmethods to empty set so we can instantiate ABC to test
    @memory_limit(512)
    def test_pattern_matched_filepath_iterator(self, patterns: str, filepaths: List[str], expected_filepaths: List[str]) -> None:
        fs = IncrementalFileStream(dataset="dummy", provider={}, format={}, path_pattern=patterns)
        file_infos = [create_by_local_file(filepath) for filepath in filepaths]
        assert set([p.key for p in fs.pattern_matched_filepath_iterator(file_infos)]) == set(expected_filepaths)

    @pytest.mark.parametrize(
        "latest_record, current_stream_state, expected",
        [
            (  # overwrite history file
                {"id": 1, "_ab_source_file_last_modified": "2022-05-11T11:54:11Z", "_ab_source_file_url": "new_test_file.csv"},
                {"_ab_source_file_last_modified": "2021-07-25T15:33:04Z", "history": {"2021-07-25": {"old_test_file.csv"}}},
                {"2022-05-11": {"new_test_file.csv"}},
            ),
            (  # add file to same day
                {"id": 1, "_ab_source_file_last_modified": "2022-07-25T11:54:11Z", "_ab_source_file_url": "new_test_file.csv"},
                {"_ab_source_file_last_modified": "2022-07-25T00:00:00Z", "history": {"2022-07-25": {"old_test_file.csv"}}},
                {"2022-07-25": {"new_test_file.csv", "old_test_file.csv"}},
            ),
            (  # add new day to history
                {"id": 1, "_ab_source_file_last_modified": "2022-07-03T11:54:11Z", "_ab_source_file_url": "new_test_file.csv"},
                {"_ab_source_file_last_modified": "2022-07-01T00:00:00Z", "history": {"2022-07-01": {"old_test_file.csv"}}},
                {"2022-07-01": {"old_test_file.csv"}, "2022-07-03": {"new_test_file.csv"}},
            ),
            (  # history size limit reached
                {"_ab_source_file_url": "test.csv"},
                {"_ab_source_file_last_modified": "2022-07-01T00:00:00Z", "history": mock_big_size_object()},
                None,
            ),
        ],
        ids=["overwrite_history_file", "add_file_to_same_day ", "add_new_day_to_history", "history_size_limit_reached"],
    )
    @patch(
        "source_s3.source_files_abstract.stream.IncrementalFileStream.__abstractmethods__", set()
    )  # patching abstractmethods to empty set so we can instantiate ABC to test
    def test_get_updated_history(self, latest_record, current_stream_state, expected, request) -> None:
        fs = IncrementalFileStream(dataset="dummy", provider={}, format={"filetype": "csv"}, path_pattern="**/prefix*.csv")
        fs._get_schema_map = MagicMock(return_value={})
        assert fs.get_updated_state(current_stream_state, latest_record).get("history") == expected

        if request.node.callspec.id == "history_size_limit_reached":
            assert fs.sync_all_files_always

    @pytest.mark.parametrize(  # set expected_return_record to None for an expected fail
        "stream_state, expected_error",
        [
            (None, False),
            ({"_ab_source_file_last_modified": "2021-07-25T15:33:04Z"}, False),
            ({"_ab_source_file_last_modified": "2021-07-25T15:33:04Z"}, False),
            ({"_ab_source_file_last_modified": "2021-07-25"}, True),
        ],
    )
    @patch(
        "source_s3.source_files_abstract.stream.IncrementalFileStream.__abstractmethods__", set()
    )  # patching abstractmethods to empty set so we can instantiate ABC to test
    def test_get_datetime_from_stream_state(self, stream_state, expected_error):
        if not expected_error:
            assert isinstance(
                IncrementalFileStream(
                    dataset="dummy", provider={"bucket": "test-test"}, format={}, path_pattern="**/prefix*.csv"
                )._get_datetime_from_stream_state(stream_state=stream_state),
                datetime,
            )
        else:
            with pytest.raises(Exception):
                assert isinstance(
                    IncrementalFileStream(
                        dataset="dummy", provider={"bucket": "test-test"}, format={}, path_pattern="**/prefix*.csv"
                    )._get_datetime_from_stream_state(stream_state=stream_state),
                    datetime,
                )

    def test_read(self):
        stream_instance = IncrementalFileStreamS3(
            dataset="dummy", provider={"bucket": "test-test"}, format={}, path_pattern="**/prefix*.csv"
        )
        stream_instance.filepath_iterator = MagicMock()

        records = []
        slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
        for slice in slices:
            records.extend(
                list(
                    stream_instance.read_records(
                        stream_slice=slice,
                        sync_mode=SyncMode.full_refresh,
                        stream_state={"_ab_source_file_last_modified": "1999-01-01T00:00:00Z"},
                    )
                )
            )

        assert not records

    @patch(
        "source_s3.source_files_abstract.stream.StorageFile.__abstractmethods__", set()
    )  # patching abstractmethods to empty set so we can instantiate ABC to test
    def test_storage_file(self):
        size = 1
        date = datetime.now()
        file_info = FileInfo(key="", size=size, last_modified=date)
        assert StorageFile(file_info=file_info, provider={}).last_modified == date
        assert StorageFile(file_info=file_info, provider={}).file_size == size
        assert file_info.size_in_megabytes == size / 1024**2
        assert file_info.__str__()
        assert file_info.__repr__()
        assert file_info == file_info
        assert not file_info < file_info

    def test_incremental_read(self):
        stream_instance = IncrementalFileStreamS3(
            dataset="dummy", provider={"bucket": "test-test"}, format={}, path_pattern="**/prefix*.csv"
        )
        stream_instance.filepath_iterator = MagicMock()

        records = []
        slices = stream_instance.stream_slices(sync_mode=SyncMode.incremental, stream_state={})

        for slice in slices:
            records.extend(list(stream_instance.read_records(stream_slice=slice, sync_mode=SyncMode.incremental)))

        assert not records

    def test_fileformatparser_map(self):
        stream_instance = IncrementalFileStreamS3(
            dataset="dummy", provider={"bucket": "test-test"}, format={}, path_pattern="**/prefix*.csv"
        )
        assert stream_instance.file_formatparser_map

    @pytest.mark.parametrize(
        ("bucket", "path_prefix", "list_v2_objects", "expected_file_info"),
        (
            (  # two files in the first response, one in the second
                "test_bucket",
                "/widescreen",
                [
                    {
                        "Contents": [
                            {"Key": "Key_A", "Size": 2048, "LastModified": datetime(2020, 2, 20, 20, 0, 2, tzinfo=timezone.utc)},
                            {"Key": "Key_B", "Size": 1024, "LastModified": datetime(2020, 2, 20, 20, 22, 2, tzinfo=timezone.utc)},
                        ],
                        "NextContinuationToken": "token",
                    },
                    {"Contents": [{"Key": "Key_C", "Size": 512, "LastModified": datetime(2022, 2, 2, 2, 2, 2, tzinfo=timezone.utc)}]},
                ],
                [
                    FileInfo(key="Key_A", size=2048, last_modified=datetime(2020, 2, 20, 20, 0, 2, tzinfo=timezone.utc)),
                    FileInfo(key="Key_B", size=1024, last_modified=datetime(2020, 2, 20, 20, 22, 2, tzinfo=timezone.utc)),
                    FileInfo(key="Key_C", size=512, last_modified=datetime(2022, 2, 2, 2, 2, 2, tzinfo=timezone.utc)),
                ],
            ),
            ("another_test_bucket", "/fullscreen", [{}], []),  # empty response
            (  # some keys are not accepted
                "almost_real_test_bucket",
                "/HD",
                [
                    {
                        "Contents": [
                            {"Key": "file/path", "Size": 2048, "LastModified": datetime(2020, 2, 20, 20, 0, 2, tzinfo=timezone.utc)},
                            {"Key": "file/path/A/", "Size": 1024, "LastModified": datetime(2020, 2, 20, 20, 22, 2, tzinfo=timezone.utc)},
                        ],
                        "NextContinuationToken": "token",
                    },
                    {"Contents": [{"Key": "file/path/B/", "Size": 512, "LastModified": datetime(2022, 2, 2, 2, 2, 2, tzinfo=timezone.utc)}]},
                ],
                [
                    FileInfo(key="file/path", size=2048, last_modified=datetime(2020, 2, 20, 20, 0, 2, tzinfo=timezone.utc)),
                ],
            ),
        ),
    )
    def test_filepath_iterator(self, bucket, path_prefix, list_v2_objects, expected_file_info):
        provider = {"aws_access_key_id": "key_id", "aws_secret_access_key": "access_key"}
        s3_client_mock = MagicMock(return_value=MagicMock(list_objects_v2=MagicMock(side_effect=list_v2_objects)))
        with patch("source_s3.stream.make_s3_client", s3_client_mock):
            stream_instance = IncrementalFileStreamS3(
                dataset="dummy",
                provider={"bucket": bucket, "path_prefix": path_prefix, **provider},
                format={},
                path_pattern="**/prefix*.png",
            )
            expected_info = iter(expected_file_info)

            for file_info in stream_instance.filepath_iterator():
                assert file_info == next(expected_info)

    @pytest.mark.parametrize(
        ("start_date", "bucket", "path_prefix", "list_v2_objects", "expected_files_count"),
        (
                ("2021-01-01T00:00:00Z",
                 "test_bucket",
                 "/widescreen",
                 [
                     {
                         "Contents": [
                             {"Key": "Key_A", "Size": 2048,
                              "LastModified": datetime(2020, 2, 20, 20, 0, 2, tzinfo=timezone.utc)},
                             {"Key": "Key_B", "Size": 1024,
                              "LastModified": datetime(2020, 2, 20, 20, 22, 2, tzinfo=timezone.utc)},
                         ],
                         "NextContinuationToken": "token",
                     },
                     {"Contents": [{"Key": "Key_C", "Size": 512,
                                    "LastModified": datetime(2022, 2, 2, 2, 2, 2, tzinfo=timezone.utc)}]},
                 ],
                 1,
                 ),
                ("2023-01-01T00:00:00Z",
                 "almost_real_test_bucket",
                 "/HD",
                 [
                     {
                         "Contents": [
                             {"Key": "file/path", "Size": 2048,
                              "LastModified": datetime(2020, 2, 20, 20, 0, 2, tzinfo=timezone.utc)},
                             {"Key": "file/path/A/", "Size": 1024,
                              "LastModified": datetime(2020, 2, 20, 20, 22, 2, tzinfo=timezone.utc)},
                         ],
                         "NextContinuationToken": "token",
                     },
                     {"Contents": [{"Key": "file/path/B/", "Size": 512,
                                    "LastModified": datetime(2022, 2, 2, 2, 2, 2, tzinfo=timezone.utc)}]},
                 ],
                 0,
                 ),
        ),
    )
    def test_filepath_iterator_date_filter(self, start_date, bucket, path_prefix, list_v2_objects, expected_files_count):
        provider = {"aws_access_key_id": "key_id", "aws_secret_access_key": "access_key"}
        s3_client_mock = MagicMock(return_value=MagicMock(list_objects_v2=MagicMock(side_effect=list_v2_objects)))
        with patch("source_s3.stream.make_s3_client", s3_client_mock):
            stream_instance = IncrementalFileStreamS3(
                dataset="dummy",
                provider={"bucket": bucket, "path_prefix": path_prefix, "start_date":start_date, **provider},
                format={},
                path_pattern="**/prefix*.png"
            )
            assert len(list(stream_instance.filepath_iterator())) == expected_files_count

    def test_get_schema(self):
        stream_instance = IncrementalFileStreamS3(
            dataset="dummy",
            provider={},
            format={"filetype": "csv"},
            schema="{\"column_A\": \"string\", \"column_B\": \"integer\", \"column_C\": \"boolean\"}",
            path_pattern="**/prefix*.csv"
        )
        assert stream_instance._schema == {
            "_ab_source_file_last_modified": {"type": "string"},
            "_ab_source_file_url": {"type": "string"},
            "column_A": "string",
            "column_B": "integer",
            "column_C": "boolean",
        }

    @pytest.mark.parametrize(
        ("file_type", "error_expected"),
        (
            (
                "csv",
                False,
            ),
            ("avro", False),
            ("parquet", False),
            ("png", True),
        ),
    )
    def test_fileformatparser_class(self, file_type, error_expected):
        stream_instance = IncrementalFileStreamS3(
            dataset="dummy", provider={}, format={"filetype": file_type}, schema={}, path_pattern="**/prefix*.csv"
        )
        if error_expected:
            with pytest.raises(RuntimeError):
                _ = stream_instance.fileformatparser_class
        else:
            assert stream_instance.fileformatparser_class

    def test_get_json_schema(self):
        stream_instance = IncrementalFileStreamS3(
            dataset="dummy",
            provider={},
            format={"filetype": "csv"},
            schema="{\"column_A\": \"string\", \"column_B\": \"integer\", \"column_C\": \"boolean\"}",
            path_pattern="**/prefix*.csv"
        )
        assert stream_instance.get_json_schema() == {
            "properties": {
                "_ab_source_file_last_modified": {"format": "date-time", "type": "string"},
                "_ab_source_file_url": {"type": "string"},
                "column_A": {"type": ["null", "string"]},
                "column_B": {"type": ["null", "integer"]},
                "column_C": {"type": ["null", "boolean"]},
            },
            "type": "object",
        }

    def test_schema_no_files(self, mocker):
        stream_instance = IncrementalFileStreamS3(
            dataset="dummy",
            provider={"bucket": "empty"},
            format={"filetype": "csv"},
            path_pattern="**/prefix*.csv"
        )
        mocker.patch.object(stream_instance, "filepath_iterator", MagicMock(return_value=[]))
        assert stream_instance.get_json_schema() == {
            "properties": {
                "_ab_source_file_last_modified": {"format": "date-time", "type": "string"},
                "_ab_source_file_url": {"type": "string"}
            },
            "type": "object",
        }

    def test_migrate_datetime_format(self):
        current_state = {"_ab_source_file_last_modified": "2022-11-09T11:12:00+0000"}
        latest_record = {"_ab_source_file_last_modified": "2020-11-09T11:12:00Z"}
        stream_instance = IncrementalFileStreamS3(
            dataset="dummy",
            provider={"bucket": "empty"},
            format={"filetype": "csv"},
            path_pattern="**/prefix*.csv"
        )
        assert stream_instance.get_updated_state(current_state, latest_record)["_ab_source_file_last_modified"] == "2022-11-09T11:12:00Z"
