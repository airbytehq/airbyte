#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import os
from copy import deepcopy
from typing import Any, Mapping
from unittest.mock import ANY

import pytest
from source_sftp_bulk import SourceSFTPBulk

from airbyte_cdk import AirbyteTracedException, ConfiguredAirbyteCatalog, Status
from airbyte_cdk.sources.declarative.models import FailureType
from airbyte_cdk.test.entrypoint_wrapper import read


logger = logging.getLogger("airbyte")


def test_check_invalid_private_key_config(configured_catalog: ConfiguredAirbyteCatalog, config_private_key_csv: Mapping[str, Any]):
    invalid_config = config_private_key_csv | {
        "credentials": {
            "auth_type": "private_key",
            "private_key": "-----BEGIN OPENSSH PRIVATE KEY-----\nbaddata\n-----END OPENSSH PRIVATE KEY-----",
        }
    }
    with pytest.raises(AirbyteTracedException) as exc_info:
        SourceSFTPBulk(catalog=configured_catalog, config=invalid_config, state=None).check(logger, invalid_config)

    assert exc_info.value.failure_type.value == FailureType.config_error.value


def test_check_invalid_config(configured_catalog: ConfiguredAirbyteCatalog, config: Mapping[str, Any]):
    invalid_config = config | {"credentials": {"auth_type": "password", "password": "wrongpass"}}
    with pytest.raises(AirbyteTracedException) as exc_info:
        SourceSFTPBulk(catalog=configured_catalog, config=invalid_config, state=None).check(logger, invalid_config)
    assert exc_info.value.failure_type.value == FailureType.config_error.value


def test_check_valid_config_private_key(configured_catalog: ConfiguredAirbyteCatalog, config_private_key: Mapping[str, Any]):
    outcome = SourceSFTPBulk(catalog=configured_catalog, config=config_private_key, state=None).check(logger, config_private_key)
    assert outcome.status == Status.SUCCEEDED


def test_check_valid_config(configured_catalog: ConfiguredAirbyteCatalog, config: Mapping[str, Any]):
    outcome = SourceSFTPBulk(catalog=configured_catalog, config=config, state=None).check(logger, config)
    assert outcome.status == Status.SUCCEEDED


def test_get_one_file_csv(configured_catalog: ConfiguredAirbyteCatalog, config: Mapping[str, Any]):
    source = SourceSFTPBulk(catalog=configured_catalog, config=config, state=None)
    output = read(source=source, config=config, catalog=configured_catalog)
    assert len(output.records) == 2


def test_get_all_files_csv(configured_catalog: ConfiguredAirbyteCatalog, config_password_all_csv: Mapping[str, Any]):
    source = SourceSFTPBulk(catalog=configured_catalog, config=config_password_all_csv, state=None)
    output = read(source=source, config=config_password_all_csv, catalog=configured_catalog)
    assert len(output.records) == 4


def test_get_files_pattern_json_new_separator(configured_catalog: ConfiguredAirbyteCatalog, config_password_all_jsonl: Mapping[str, Any]):
    source = SourceSFTPBulk(catalog=configured_catalog, config=config_password_all_jsonl, state=None)
    output = read(source=source, config=config_password_all_jsonl, catalog=configured_catalog)
    assert len(output.records) == 3


def test_get_all_files_excel_xlsx(configured_catalog: ConfiguredAirbyteCatalog, config_password_all_excel_xlsx: Mapping[str, Any]):
    source = SourceSFTPBulk(catalog=configured_catalog, config=config_password_all_excel_xlsx, state=None)
    output = read(source=source, config=config_password_all_excel_xlsx, catalog=configured_catalog)
    assert len(output.records) == 2


def test_get_all_files_excel_xls(configured_catalog: ConfiguredAirbyteCatalog, config_password_all_excel_xls: Mapping[str, Any]):
    source = SourceSFTPBulk(catalog=configured_catalog, config=config_password_all_excel_xls, state=None)
    output = read(source=source, config=config_password_all_excel_xls, catalog=configured_catalog)
    assert len(output.records) == 1


def test_get_files_pattern_no_match_json(configured_catalog: ConfiguredAirbyteCatalog, config_password_all_jsonl: Mapping[str, Any]):
    config_with_wrong_glob_pattern = deepcopy(config_password_all_jsonl)
    config_with_wrong_glob_pattern["streams"][0]["globs"] = ["**/not_existed_file.jsonl"]
    source = SourceSFTPBulk(catalog=configured_catalog, config=config_with_wrong_glob_pattern, state=None)
    output = read(source=source, config=config_with_wrong_glob_pattern, catalog=configured_catalog)
    assert len(output.records) == 0


def test_get_files_empty_files(configured_catalog: ConfiguredAirbyteCatalog, config_password_all_jsonl: Mapping[str, Any]):
    config_with_wrong_glob_pattern = deepcopy(config_password_all_jsonl)
    config_with_wrong_glob_pattern["streams"][0]["globs"] = ["**/files/empty/*.jsonl"]
    source = SourceSFTPBulk(catalog=configured_catalog, config=config_with_wrong_glob_pattern, state=None)
    output = read(source=source, config=config_with_wrong_glob_pattern, catalog=configured_catalog)
    assert len(output.records) == 0


@pytest.mark.slow
@pytest.mark.limit_memory("10 MB")
def test_get_file_csv_file_transfer(configured_catalog: ConfiguredAirbyteCatalog, config_fixture_use_file_transfer: Mapping[str, Any]):
    source = SourceSFTPBulk(catalog=configured_catalog, config=config_fixture_use_file_transfer, state=None)
    output = read(source=source, config=config_fixture_use_file_transfer, catalog=configured_catalog)
    expected_file_data = {
        "bytes": 46_754_266,
        "file_relative_path": "files/file_transfer/file_transfer_1.csv",
        "file_url": "/tmp/airbyte-file-transfer/files/file_transfer/file_transfer_1.csv",
        "modified": ANY,
        "source_file_url": "/files/file_transfer/file_transfer_1.csv",
    }
    assert len(output.records) == 1
    assert list(map(lambda record: record.record.file, output.records)) == [expected_file_data]

    # Additional assertion to check if the file exists at the file_url path
    file_path = expected_file_data["file_url"]
    assert os.path.exists(file_path), f"File not found at path: {file_path}"


@pytest.mark.slow
@pytest.mark.limit_memory("10 MB")
def test_get_all_file_csv_file_transfer(
    configured_catalog: ConfiguredAirbyteCatalog, config_fixture_use_all_files_transfer: Mapping[str, Any]
):
    """
    - The Paramiko dependency `get` method uses requests parallelization for efficiency, which may slightly increase memory usage.
    - The test asserts that this memory increase remains below the files sizes being transferred.
    """
    source = SourceSFTPBulk(catalog=configured_catalog, config=config_fixture_use_all_files_transfer, state=None)
    output = read(source=source, config=config_fixture_use_all_files_transfer, catalog=configured_catalog)
    assert len(output.records) == 5
    total_bytes = sum(list(map(lambda record: record.record.file["bytes"], output.records)))
    files_paths = list(map(lambda record: record.record.file["file_url"], output.records))
    for file_path in files_paths:
        assert os.path.exists(file_path), f"File not found at path: {file_path}"
    assert total_bytes == 233_771_330
