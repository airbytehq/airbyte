import os
from click.testing import CliRunner

from typing import List
from metadata_service.validators.metadata_validator import validate_metadata_file


def get_all_valid_metadata_yaml_files() -> List[str]:
    file_path = os.path.join(os.path.dirname(__file__), "fixtures", "valid")
    # list the absolute paths of all files in the directory
    return [os.path.join(file_path, file_name) for file_name in os.listdir(file_path)]


def get_all_invalid_metadata_yaml_files() -> List[str]:
    file_path = os.path.join(os.path.dirname(__file__), "fixtures", "invalid")
    # list the absolute paths of all files in the directory
    return [os.path.join(file_path, file_name) for file_name in os.listdir(file_path)]


def test_valid_metadata_yaml_files():
    runner = CliRunner()
    valid_file_paths = get_all_valid_metadata_yaml_files()

    assert len(valid_file_paths) > 0, "No files found"

    for file_path in valid_file_paths:
        result = runner.invoke(validate_metadata_file, [file_path])
        assert result.exit_code == 0, f"Validation failed for {file_path} with error: {result.output}"


def test_invalid_metadata_yaml_files():
    runner = CliRunner()
    invalid_file_paths = get_all_invalid_metadata_yaml_files()

    assert len(invalid_file_paths) > 0, "No files found"

    for file_path in invalid_file_paths:
        result = runner.invoke(validate_metadata_file, [file_path])
        assert result.exit_code == 1, f"Validation succeeded (when it shouldve failed) for {file_path}"


def test_file_not_found_fails():
    runner = CliRunner()
    result = runner.invoke(validate_metadata_file, ["non_existent_file.yaml"])
    assert result.exit_code == 1, "Validation succeeded (when it shouldve failed) for non_existent_file.yaml"
