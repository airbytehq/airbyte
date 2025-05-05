#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import os
import shutil
import tempfile
from copy import deepcopy
from typing import Any, Mapping
from unittest.mock import ANY, patch

import gnupg
import pytest
from source_sftp_bulk import SourceSFTPBulk

from airbyte_cdk import AirbyteTracedException, ConfiguredAirbyteCatalog, Status
from airbyte_cdk.models import (
    FailureType,
    Status,
)
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


def test_default_mirroring_paths_works_for_not_present_config_file_transfer(
    configured_catalog: ConfiguredAirbyteCatalog, config_fixture_not_duplicates: Mapping[str, Any]
):
    """
    If delivery_options is not provided in the config we fall back preserve directories (mirroring paths).
    """
    expected_directory_path = "files/not_duplicates/data/"
    expected_uniqueness_count = 3
    source = SourceSFTPBulk(catalog=configured_catalog, config=config_fixture_not_duplicates, state=None)
    output = read(source=source, config=config_fixture_not_duplicates, catalog=configured_catalog)
    assert len(output.records) == expected_uniqueness_count
    files_paths = set(map(lambda record: record.record.file["file_url"], output.records))
    files_relative_paths = set(map(lambda record: record.record.file["file_relative_path"], output.records))
    assert len(files_relative_paths) == expected_uniqueness_count
    assert len(files_paths) == expected_uniqueness_count
    for file_path, files_relative_path in zip(files_paths, files_relative_paths):
        assert expected_directory_path in file_path, f"File not found at path: {file_path}"
        assert expected_directory_path in files_relative_path, f"File not found at path: {files_relative_path}"


def test_not_mirroring_paths_not_duplicates_file_transfer(
    configured_catalog: ConfiguredAirbyteCatalog, config_fixture_not_mirroring_paths_not_duplicates: Mapping[str, Any]
):
    """
    Delivery options is present and preserve_directory_structure is False so we should not preserve directories (mirroring paths).
    """
    source_directory_path = "files/not_duplicates/data/"
    expected_uniqueness_count = 3
    source = SourceSFTPBulk(catalog=configured_catalog, config=config_fixture_not_mirroring_paths_not_duplicates, state=None)
    output = read(source=source, config=config_fixture_not_mirroring_paths_not_duplicates, catalog=configured_catalog)
    assert len(output.records) == expected_uniqueness_count
    files_paths = set(map(lambda record: record.record.file["file_url"], output.records))
    files_relative_paths = set(map(lambda record: record.record.file["file_relative_path"], output.records))
    assert len(files_relative_paths) == expected_uniqueness_count
    assert len(files_paths) == expected_uniqueness_count
    for file_path, files_relative_path in zip(files_paths, files_relative_paths):
        assert source_directory_path not in file_path, f"Source path found but mirroring is off: {file_path}"
        assert source_directory_path not in files_relative_path, f"Source path found but mirroring is off: {files_relative_path}"


def test_not_mirroring_paths_with_duplicates_file_transfer_fails_sync(
    configured_catalog: ConfiguredAirbyteCatalog, config_fixture_not_mirroring_paths_with_duplicates: Mapping[str, Any]
):
    """
    Delivery options is present and preserve_directory_structure is False so we should not preserve directories (mirroring paths),
    but, there are duplicates so the sync fails.
    """

    source = SourceSFTPBulk(catalog=configured_catalog, config=config_fixture_not_mirroring_paths_with_duplicates, state=None)
    output = read(source=source, config=config_fixture_not_mirroring_paths_with_duplicates, catalog=configured_catalog)

    # assert error_message in output.errors[-1].trace.error.message
    assert "3 duplicates found for file name monthly-kickoff.mpeg" in output.errors[-1].trace.error.message
    assert "/files/duplicates/data/feb/monthly-kickoff.mpeg" in output.errors[-1].trace.error.message
    assert "/files/duplicates/data/jan/monthly-kickoff.mpeg" in output.errors[-1].trace.error.message
    assert "/files/duplicates/data/mar/monthly-kickoff.mpeg" in output.errors[-1].trace.error.message
    assert not output.records


# =============== GPG DECRYPTION TESTS ===============

@pytest.fixture(name="gpg_keyring")
def gpg_keyring_fixture():
    """Fixture for creating a temporary GPG keyring with a test key pair"""
    # Create a temporary directory for the GPG keyring
    gnupghome = tempfile.mkdtemp(prefix="gnupg_test_")
    
    # Initialize GPG with the temporary home directory
    gpg = gnupg.GPG(gnupghome=gnupghome)
    
    # Generate a key pair
    key_params = {
        'name_real': 'Test User',
        'name_email': 'test@example.com',
        'key_type': 'RSA',
        'key_length': 2048,
        'key_usage': 'encrypt,sign',
        'passphrase': 'test-passphrase'
    }
    
    # Generate the key
    key = gpg.gen_key(gpg.gen_key_input(**key_params))
    
    # Export the private key
    private_key = gpg.export_keys(key.fingerprint, True, passphrase=key_params['passphrase'])
    
    # Export the public key
    public_key = gpg.export_keys(key.fingerprint)
    
    # Create a dictionary with the key information
    key_info = {
        'fingerprint': key.fingerprint,
        'private_key': private_key,
        'public_key': public_key,
        'passphrase': key_params['passphrase'],
        'gnupghome': gnupghome,
        'gpg': gpg
    }
    
    yield key_info
    
    # Clean up the temporary directory
    shutil.rmtree(gnupghome)


@pytest.fixture(name="encrypt_test_file")
def encrypt_test_file_fixture(gpg_keyring, config):
    """Fixture to create and encrypt a test file using GPG"""
    # Create a temporary directory to store the encrypted file
    temp_dir = tempfile.mkdtemp(prefix="gpg_test_files_")
    
    # Determine the target directory on the SFTP server
    target_dir = os.path.join("/files", "gpg_test")
    
    # Create the test file content
    test_content = \
        """string_col,int_col
        test1,1
        test2,2
        """
    
    # Create a temporary file for the test content
    temp_file = os.path.join(temp_dir, "test_file.csv")
    with open(temp_file, "w") as f:
        f.write(test_content)
    
    # Encrypt the file
    encrypted_file = os.path.join(temp_dir, "test_file.csv.gpg")
    with open(temp_file, "rb") as f:
        gpg_keyring["gpg"].encrypt_file(
            f, 
            recipients=[gpg_keyring["fingerprint"]], 
            output=encrypted_file
        )
    
    # Create the target directory on the SFTP server if it doesn't exist
    sftp_files_dir = os.path.join(os.path.dirname(__file__), "files", "gpg_test")
    os.makedirs(sftp_files_dir, exist_ok=True)
    
    # Copy the encrypted file to the target directory
    shutil.copy(encrypted_file, os.path.join(sftp_files_dir, "test_file.csv.gpg"))
    
    # Return information about the files
    result = {
        "temp_dir": temp_dir,
        "target_dir": target_dir,
        "test_file": temp_file,
        "encrypted_file": encrypted_file,
        "sftp_path": os.path.join(target_dir, "test_file.csv.gpg")
    }
    
    yield result
    
    # Clean up the temporary directory
    shutil.rmtree(temp_dir)
    
    # Clean up the target directory
    try:
        shutil.rmtree(sftp_files_dir)
    except Exception as e:
        logger.warning(f"Failed to clean up target directory: {e}")


@pytest.fixture(name="config_gpg")
def config_gpg_fixture(config, gpg_keyring):
    """Fixture for creating a config with GPG decryption enabled"""
    gpg_config = config.copy()
    gpg_config["folder_path"] = "/files/gpg_test"
    
    # Add a stream configuration for CSV files
    gpg_config["streams"] = [{
        "name": "gpg_test_stream",
        "globs": ["**/*.gpg"],
        "format": {
            "filetype": "csv"
        }
    }]
    
    # Add GPG decryption configuration
    gpg_config["decryption"] = {
        "decryption_type": "gpg",
        "private_key": gpg_keyring["private_key"],
        "passphrase": gpg_keyring["passphrase"]
    }
    
    return gpg_config


def test_gpg_check_with_gpg_config(configured_catalog, config_gpg):
    """Test the check command with GPG decryption enabled"""
    source = SourceSFTPBulk(catalog=configured_catalog, config=config_gpg, state=None)
    outcome = source.check(logger, config_gpg)
    assert outcome.status == Status.SUCCEEDED


def test_gpg_read_with_gpg_decryption(configured_catalog, config_gpg, encrypt_test_file):
    """Test reading an encrypted file with GPG decryption enabled"""
    source = SourceSFTPBulk(catalog=configured_catalog, config=config_gpg, state=None)
    output = read(source=source, config=config_gpg, catalog=configured_catalog)
    
    # Check that we have records
    assert len(output.records) > 0
    
    # Check that the records contain the expected data
    record_data = [r.record.data for r in output.records]
    assert "string_col" in record_data[0]
    assert "int_col" in record_data[0]
    
    # Check values in the first record
    assert record_data[0]["string_col"] == "test1"
    assert record_data[0]["int_col"] == 1
    
    # Check values in the second record
    assert record_data[1]["string_col"] == "test2"
    assert record_data[1]["int_col"] == 2


def test_gpg_get_file_with_gpg_decryption(configured_catalog, config_gpg, encrypt_test_file):
    """Test raw file transfer with GPG decryption enabled"""
    # Update config to use file transfer instead of records
    config_file_transfer = config_gpg.copy()
    config_file_transfer["delivery_method"] = {
        "delivery_type": "use_file_transfer",
        "preserve_directory_structure": True
    }
    
    source = SourceSFTPBulk(catalog=configured_catalog, config=config_file_transfer, state=None)
    output = read(source=source, config=config_file_transfer, catalog=configured_catalog)
    
    # Check that we have records
    assert len(output.records) > 0
    
    # Extract file information from the record
    record = output.records[0].record
    assert "file" in record.__dict__
    file_info = record.file
    
    # Check that the file has been decrypted (no .gpg extension)
    assert not file_info["file_url"].endswith(".gpg")
    assert os.path.exists(file_info["file_url"])
    
    # Read the decrypted file content and verify
    with open(file_info["file_url"], "r") as f:
        content = f.read()
        assert "string_col,int_col" in content
        assert "test1,1" in content
        assert "test2,2" in content


def test_gpg_with_invalid_key(configured_catalog, config_gpg):
    """Test GPG decryption with an invalid key"""
    # Create a config with an invalid GPG key
    invalid_config = config_gpg.copy()
    invalid_config["decryption"] = {
        "decryption_type": "gpg",
        "private_key": "-----BEGIN PGP PRIVATE KEY BLOCK-----\nInvalid Key\n-----END PGP PRIVATE KEY BLOCK-----",
        "passphrase": "wrong-passphrase"
    }
    
    # The check should fail with a configuration error
    source = SourceSFTPBulk(catalog=configured_catalog, config=invalid_config, state=None)
    
    with pytest.raises(AirbyteTracedException) as exc_info:
        source.check(logger, invalid_config)
    
    # Verify the error message
    assert "Failed to import GPG private key" in str(exc_info.value)