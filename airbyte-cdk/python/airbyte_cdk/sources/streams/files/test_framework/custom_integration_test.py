#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
import os
import time
from abc import ABC, abstractmethod
from typing import Any, Iterator, List, Mapping
from uuid import uuid4

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.files import FilesStream
from airbyte_cdk.sources.streams.files.formats.csv_parser import CsvParser

from .sample_files import SAMPLE_DIR

LOGGER = logging.getLogger("airbyte")
JSONTYPE_TO_PYTHONTYPE = {"string": str, "number": float, "integer": int, "object": dict, "array": list, "boolean": bool, "null": None}


class AbstractFilesStreamIntegrationTest(ABC):
    """Prefix this class with Abstract so the tests don't run here but only in the children"""

    temp_bucket_prefix = "airbytetest-"

    @pytest.fixture(scope="session")
    def cloud_bucket_prefix(self) -> str:
        return self.temp_bucket_prefix

    @pytest.fixture(scope="session")
    def format(self) -> Mapping[str, Any]:
        return {"filetype": "csv"}

    @pytest.fixture(scope="session")
    def airbyte_system_columns(self) -> Mapping[str, str]:
        return {FilesStream.ab_additional_col: "object", FilesStream.ab_last_mod_col: "string", FilesStream.ab_file_name_col: "string"}

    @property
    @abstractmethod
    def stream_class(self) -> type:
        """
        :return: provider specific FilesStream class
        """

    @property
    @abstractmethod
    def credentials(self) -> Mapping:
        """
        These will be added automatically to the provider property

        :return: mapping of provider specific credentials
        """

    @abstractmethod
    def provider(self, bucket_name: str) -> Mapping:
        """
        :return: provider specific provider dict as described in spec.json
                 leave out the credentials, they will be added from the credentials() method
        """

    @abstractmethod
    def cloud_files(self, cloud_bucket_name: str, credentials: Mapping, files_to_upload: List, private: bool = True) -> Iterator[str]:
        """
        See source-s3 for example what the override of this needs to achieve.

        :param cloud_bucket_name: name of bucket (or equivalent)
        :param credentials: mapping of provider specific credentials
        :param files_to_upload: list of paths to local files to upload, pass empty list to test zero files case
        :param private: whether or not to make the files private and require credentials to read, defaults to True
        :yield: url filepath to uploaded file
        """

    @abstractmethod
    def teardown_infra(self, cloud_bucket_name: str, credentials: Mapping) -> None:
        """
        Provider-specific logic to tidy up any cloud resources.
        See source-s3 for example.

        :param cloud_bucket_name: bucket (or equivalent) name
        :param credentials: mapping of provider specific credentials
        """

    def _stream_records_test_logic(
        self,
        cloud_bucket_name: str,
        format: Mapping[str, str],
        airbyte_system_columns: Mapping[str, str],
        sync_mode: Any,
        files: List[str],
        path_pattern: str,
        private: bool,
        num_columns: Any,
        num_records: Any,
        expected_schema: Mapping[str, Any],
        user_schema: Mapping[str, Any],
        fails: Any,
        state: Any = None,
    ) -> Any:
        uploaded_files = [fpath for fpath in self.cloud_files(cloud_bucket_name, self.credentials, files, private)]
        LOGGER.info(f"file(s) uploaded: {uploaded_files}")

        # emulate state for incremental testing
        # since we're not actually saving state out to file here, we pass schema in to our FileStream creation...
        # this isn't how it will work in Airbyte but it's a close enough emulation
        current_state = state if state is not None else {FilesStream.ab_last_mod_col: "1970-01-01T00:00:00+0000"}
        if (user_schema is None) and ("schema" in current_state.keys()):
            user_schema = current_state["schema"]

        full_expected_schema = {**expected_schema, **airbyte_system_columns}
        str_user_schema = str(user_schema).replace("'", '"') if user_schema is not None else None
        total_num_columns = num_columns + len(airbyte_system_columns.keys())
        provider = {**self.provider(cloud_bucket_name), **self.credentials} if private else self.provider(cloud_bucket_name)

        if not fails:
            stream = self.stream_class("dataset", provider, format, path_pattern, str_user_schema)
            LOGGER.info(f"Testing stream_records() in SyncMode:{sync_mode.value}")

            # check we return correct schema from get_json_schema()
            assert stream._get_schema_map() == full_expected_schema

            records = []
            for stream_slice in stream.stream_slices(sync_mode=sync_mode, stream_state=current_state):
                if stream_slice is not None:
                    # we need to do this in order to work out which extra columns (if any) we expect in this stream_slice
                    expected_columns = []
                    for file_dict in stream_slice["files"]:
                        file_reader = CsvParser(format)
                        with file_dict["storage_file"].open(file_reader.is_binary) as f:
                            expected_columns.extend(list(file_reader.get_inferred_schema(f).keys()))
                    expected_columns = set(expected_columns)  # de-dupe

                    for record in stream.read_records(sync_mode, stream_slice=stream_slice):
                        # check actual record values match expected schema
                        assert all(
                            [
                                isinstance(record[col], JSONTYPE_TO_PYTHONTYPE[typ]) or record[col] is None
                                for col, typ in full_expected_schema.items()
                            ]
                        )
                        records.append(record)

            assert all([len(r.keys()) == total_num_columns for r in records])
            assert len(records) == num_records

            # check additional properties included as expected if any exist
            if (user_schema is not None) and (expected_columns != set(user_schema.keys())):
                for additional_property in expected_columns.difference(set(user_schema.keys())):
                    # since we can't be dynamically aware of which records should have which additional props, we just any() check here
                    assert any([additional_property in r[FilesStream.ab_additional_col].keys() for r in records])

            # returning state by simulating call to get_updated_state() with final record so we can test incremental
            return stream.get_updated_state(current_stream_state=current_state, latest_record=records[-1])

        else:
            with pytest.raises(Exception) as e_info:
                stream = self.stream_class("dataset", provider, format, path_pattern, str_user_schema)
                LOGGER.info(f"Testing EXPECTED FAILURE stream_records() in SyncMode:{sync_mode.value}")

                stream.get_json_schema()

                records = []
                for stream_slice in stream.stream_slices(sync_mode=sync_mode, stream_state=current_state):
                    for record in stream.read_records(sync_mode, stream_slice=stream_slice):
                        records.append(record)

                LOGGER.info(f"Failed as expected, error: {e_info}")

    @pytest.mark.parametrize(
        # make user_schema None to test auto-inference. Exclude any _airbyte system columns in expected_schema.
        "files, path_pattern, private, num_columns, num_records, expected_schema, user_schema, incremental, fails",
        [
            # single file tests
            (  # public
                [os.path.join(SAMPLE_DIR, "simple_test.csv")],
                "**",
                False,
                3,
                8,
                {"id": "integer", "name": "string", "valid": "boolean"},
                None,
                False,
                False,
            ),
            (  # private
                [os.path.join(SAMPLE_DIR, "simple_test.csv")],
                "**",
                True,
                3,
                8,
                {"id": "integer", "name": "string", "valid": "boolean"},
                None,
                False,
                False,
            ),
            (  # provided schema exact match to actual schema
                [os.path.join(SAMPLE_DIR, "simple_test.csv")],
                "**",
                True,
                3,
                8,
                {"id": "integer", "name": "string", "valid": "boolean"},
                {"id": "integer", "name": "string", "valid": "boolean"},
                False,
                False,
            ),
            (  # provided schema not matching datatypes, expect successful coercion
                [os.path.join(SAMPLE_DIR, "simple_test.csv")],
                "**",
                True,
                3,
                8,
                {"id": "string", "name": "string", "valid": "string"},
                {"id": "string", "name": "string", "valid": "string"},
                False,
                False,
            ),
            (  # provided incompatible schema, expect fail
                [os.path.join(SAMPLE_DIR, "simple_test.csv")],
                "**",
                True,
                3,
                8,
                {"id": "boolean", "name": "boolean", "valid": "boolean"},
                {"id": "boolean", "name": "boolean", "valid": "boolean"},
                False,
                True,
            ),
            # multiple file tests (all have identical schemas)
            (  # public, auto-infer
                [
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_2.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_3.csv"),
                ],
                "**",
                False,
                3,
                17,
                {"id": "integer", "name": "string", "valid": "boolean"},
                None,
                False,
                False,
            ),
            (  # private, auto-infer
                [
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_2.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_3.csv"),
                ],
                "**",
                True,
                3,
                17,
                {"id": "integer", "name": "string", "valid": "boolean"},
                None,
                False,
                False,
            ),
            (  # provided schema exact match to actual schema
                [
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_2.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_3.csv"),
                ],
                "**",
                True,
                3,
                17,
                {"id": "integer", "name": "string", "valid": "boolean"},
                {"id": "integer", "name": "string", "valid": "boolean"},
                False,
                False,
            ),
            (  # provided schema not matching datatypes, expect successful coercion
                [
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_2.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_3.csv"),
                ],
                "**",
                True,
                3,
                17,
                {"id": "string", "name": "string", "valid": "string"},
                {"id": "string", "name": "string", "valid": "string"},
                False,
                False,
            ),
            (  # provided incompatible schema, expect fail
                [
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_2.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_3.csv"),
                ],
                "**",
                True,
                3,
                17,
                {"id": "boolean", "name": "boolean", "valid": "boolean"},
                {"id": "boolean", "name": "boolean", "valid": "boolean"},
                False,
                True,
            ),
            # multiple file tests (different but merge-able schemas)
            (  # auto-infer
                [
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                    os.path.join(SAMPLE_DIR, "multi_file_diffschema_1.csv"),
                    os.path.join(SAMPLE_DIR, "multi_file_diffschema_2.csv"),
                ],
                "**",
                True,
                6,
                17,
                {"id": "integer", "name": "string", "valid": "boolean", "location": "string", "percentage": "number", "nullable": "string"},
                None,
                False,
                False,
            ),
            (  # provided schema, not containing all columns (extra columns should go into FileStream.ab_additional_col)
                [
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                    os.path.join(SAMPLE_DIR, "multi_file_diffschema_1.csv"),
                    os.path.join(SAMPLE_DIR, "multi_file_diffschema_2.csv"),
                ],
                "**",
                True,
                3,
                17,
                {"id": "integer", "name": "string", "valid": "boolean"},
                {"id": "integer", "name": "string", "valid": "boolean"},
                False,
                False,
            ),
            # pattern matching tests with additional files present that we don't want to read
            (  # at top-level of bucket
                [
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_2.csv"),
                    os.path.join(SAMPLE_DIR, "file_to_skip.csv"),
                    os.path.join(SAMPLE_DIR, "file_to_skip.txt"),
                ],
                "simple*",
                True,
                3,
                11,
                {"id": "integer", "name": "string", "valid": "boolean"},
                None,
                False,
                False,
            ),
            (  # at multiple levels of bucket
                [
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_2.csv"),
                    os.path.join(SAMPLE_DIR, "file_to_skip.csv"),
                    os.path.join(SAMPLE_DIR, "file_to_skip.txt"),
                    os.path.join(SAMPLE_DIR, "pattern_match_test/this_folder/simple_test.csv"),
                    os.path.join(SAMPLE_DIR, "pattern_match_test/not_this_folder/file_to_skip.csv"),
                    os.path.join(SAMPLE_DIR, "pattern_match_test/not_this_folder/file_to_skip.txt"),
                ],
                "**/simple*",
                True,
                3,
                19,
                {"id": "integer", "name": "string", "valid": "boolean"},
                None,
                False,
                False,
            ),
            # incremental tests (passing num_records/num_columns/fails as lists holding value for each file in order)
            (  # auto-infer, all same schema
                [
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_2.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_3.csv"),
                ],
                "**",
                True,
                [3, 3, 3],
                [8, 3, 6],
                {"id": "integer", "name": "string", "valid": "boolean"},
                None,
                True,
                [False, False, False],
            ),
            (  # provided schema, all same schema
                [
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_2.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test_3.csv"),
                ],
                "**",
                True,
                [3, 3, 3],
                [8, 3, 6],
                {"id": "integer", "name": "string", "valid": "boolean"},
                {"id": "integer", "name": "string", "valid": "boolean"},
                True,
                [False, False, False],
            ),
            (  # auto-infer, (different but merge-able schemas)
                [
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                    os.path.join(SAMPLE_DIR, "multi_file_diffschema_1.csv"),
                    os.path.join(SAMPLE_DIR, "multi_file_diffschema_2.csv"),
                ],
                "**",
                True,
                [3, 3, 3],
                [8, 3, 6],
                {"id": "integer", "name": "string", "valid": "boolean"},
                None,
                True,
                [False, False, False],
            ),
            (  # same as previous but change order and expect 5 columns instead of 3 in all
                [
                    os.path.join(SAMPLE_DIR, "multi_file_diffschema_2.csv"),
                    os.path.join(SAMPLE_DIR, "multi_file_diffschema_1.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                ],
                "**",
                True,
                [5, 5, 5],
                [6, 3, 8],
                {"id": "integer", "name": "string", "valid": "boolean", "percentage": "number", "nullable": "string"},
                None,
                True,
                [False, False, False],
            ),
            (  # like previous test but with a user_schema limiting columns
                [
                    os.path.join(SAMPLE_DIR, "multi_file_diffschema_2.csv"),
                    os.path.join(SAMPLE_DIR, "multi_file_diffschema_1.csv"),
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                ],
                "**",
                True,
                [2, 2, 2],
                [6, 3, 8],
                {"id": "integer", "name": "string"},
                {"id": "integer", "name": "string"},
                True,
                [False, False, False],
            ),
            (  # fail when 2nd file has incompatible schema, auto-infer
                [
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                    os.path.join(SAMPLE_DIR, "incompatible_schema.csv"),
                ],
                "**",
                True,
                [3, 3],
                [8, 8],
                {"id": "integer", "name": "string", "valid": "boolean"},
                None,
                True,
                [False, True],
            ),
            (  # fail when 2nd file has incompatible schema, provided schema
                [
                    os.path.join(SAMPLE_DIR, "simple_test.csv"),
                    os.path.join(SAMPLE_DIR, "incompatible_schema.csv"),
                ],
                "**",
                True,
                [3, 3],
                [8, 8],
                {"id": "integer", "name": "string", "valid": "boolean"},
                {"id": "integer", "name": "string", "valid": "boolean"},
                True,
                [False, True],
            ),
        ],
    )
    def test_stream_records(
        self,
        cloud_bucket_prefix: str,
        format: Mapping[str, Any],
        airbyte_system_columns: Mapping[str, str],
        files: List[str],
        path_pattern: str,
        private: bool,
        num_columns: List[int],
        num_records: List[int],
        expected_schema: Mapping[str, Any],
        user_schema: Mapping[str, Any],
        incremental: bool,
        fails: List[bool],
    ) -> None:
        try:
            if not incremental:  # we expect matching behaviour here in either sync_mode
                for sync_mode in [
                    SyncMode("full_refresh"),
                    SyncMode("incremental"),
                ]:
                    cloud_bucket_name = f"{cloud_bucket_prefix}{uuid4()}"
                    self._stream_records_test_logic(
                        cloud_bucket_name,
                        format,
                        airbyte_system_columns,
                        sync_mode,
                        files,
                        path_pattern,
                        private,
                        num_columns,
                        num_records,
                        expected_schema,
                        user_schema,
                        fails,
                    )
                    self.teardown_infra(cloud_bucket_name, self.credentials)
            else:
                cloud_bucket_name = f"{cloud_bucket_prefix}{uuid4()}"
                latest_state = None
                for i in range(len(files)):
                    latest_state = self._stream_records_test_logic(
                        cloud_bucket_name,
                        format,
                        airbyte_system_columns,
                        SyncMode("incremental"),
                        [files[i]],
                        path_pattern,
                        private,
                        num_columns[i],
                        num_records[i],
                        expected_schema,
                        user_schema,
                        fails[i],
                        state=latest_state,
                    )
                    LOGGER.info(f"incremental state: {latest_state}")
                    # small delay to ensure next file gets later last_modified timestamp
                    time.sleep(1)
                self.teardown_infra(cloud_bucket_name, self.credentials)

        except Exception as e:
            self.teardown_infra(cloud_bucket_name, self.credentials)
            raise e
