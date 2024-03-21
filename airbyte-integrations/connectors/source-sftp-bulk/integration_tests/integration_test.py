#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Mapping

from airbyte_cdk.models import ConfiguredAirbyteCatalog, Status, Type
from airbyte_cdk.test.entrypoint_wrapper import read
from source_sftp_bulk import SourceSFTPBulk

logger = logging.getLogger("airbyte")


def test_check_invalid_private_key_config(configured_catalog: ConfiguredAirbyteCatalog, config_private_key_csv: Mapping[str, Any]):
    invalid_config = config_private_key_csv | {
        "credentials": {
            "auth_type": "private_key",
            "private_key": "-----BEGIN OPENSSH PRIVATE KEY-----\nbaddata\n-----END OPENSSH PRIVATE KEY-----",
        }
    }
    outcome = SourceSFTPBulk(catalog=configured_catalog, config=invalid_config, state=None).check(logger, invalid_config)
    assert outcome.status == Status.FAILED


def test_check_invalid_config(configured_catalog: ConfiguredAirbyteCatalog, config: Mapping[str, Any]):
    invalid_config = config | {"credentials": {"auth_type": "password", "password": "wrongpass"}}
    outcome = SourceSFTPBulk(catalog=configured_catalog, config=invalid_config, state=None).check(logger, invalid_config)
    assert outcome.status == Status.FAILED


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


def test_get_files_pattern_json_new_separator(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result_iter = source.read(logger, {**config, "file_pattern": "test_2.+"}, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 1
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] == "hello"
        assert res.record.data["int_col"] == 1


def test_get_files_pattern_no_match_json(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result = source.read(logger, {**config, "file_pattern": "bad_pattern.+"}, configured_catalog, None)
    assert len(list(result)) == 0


def test_get_files_no_pattern_csv(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result_iter = source.read(logger, {**config, "file_type": "csv", "folder_path": "files/csv"}, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 4
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_csv(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result_iter = source.read(
        logger, {**config, "file_type": "csv", "folder_path": "files/csv", "file_pattern": "test_1.+"}, configured_catalog, None
    )
    result = list(result_iter)
    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_csv_new_separator(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result_iter = source.read(
        logger, {**config, "file_type": "csv", "folder_path": "files/csv", "file_pattern": "test_2.+"}, configured_catalog, None
    )
    result = list(result_iter)
    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_csv_new_separator_with_config(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result_iter = source.read(
        logger,
        {**config, "file_type": "csv", "folder_path": "files/csv", "separator": ";", "file_pattern": "test_2.+"},
        configured_catalog,
        None,
    )
    result = list(result_iter)
    assert len(result) == 2
    for res in result:
        assert res.type == Type.RECORD
        assert res.record.data["string_col"] in ["foo", "hello"]
        assert res.record.data["int_col"] in [1, 2]


def test_get_files_pattern_no_match_csv(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result = source.read(
        logger, {**config, "file_type": "csv", "folder_path": "files/csv", "file_pattern": "badpattern.+"}, configured_catalog, None
    )
    assert len(list(result)) == 0


def test_get_files_empty_files(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result = source.read(logger, {**config, "folder_path": "files/empty"}, configured_catalog, None)
    assert len(list(result)) == 0


def test_get_files_handle_null_values(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    source = SourceSFTPBulk()
    result_iter = source.read(logger, {**config, "folder_path": "files/null_values", "file_type": "csv"}, configured_catalog, None)
    result = list(result_iter)
    assert len(result) == 5

    res = result[2]
    assert res.type == Type.RECORD
    assert res.record.data["string_col"] == "bar"
    assert res.record.data["int_col"] is None

    res = result[4]
    assert res.type == Type.RECORD
    assert res.record.data["string_col"] is None
    assert res.record.data["int_col"] == 4
