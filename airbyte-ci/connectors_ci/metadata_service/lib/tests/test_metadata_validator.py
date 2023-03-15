import json
import os
from click.testing import CliRunner

from typing import List
from metadata_service.validators.metadata_validator import validate_metadata_file


def oss_catalog_dict():
    file_path = os.path.join(os.path.dirname(__file__), "fixtures", "oss_catalog.json")
    return json.load(open(file_path))


def cloud_catalog_dict():
    file_path = os.path.join(os.path.dirname(__file__), "fixtures", "cloud_catalog.json")
    return json.load(open(file_path))

def get_all_valid_metadata_yaml_files() -> List[str]:
    file_path = os.path.join(os.path.dirname(__file__), "fixtures", "valid")
    # list the absolute paths of all files in the directory
    return [os.path.join(file_path, file_name) for file_name in os.listdir(file_path)]


def test_valid_metadata_yaml_files():
    runner = CliRunner()
    valid_file_paths = get_all_valid_metadata_yaml_files()

    assert len(valid_file_paths) > 0, "No valid metadata files found"

    for file_path in get_all_valid_metadata_yaml_files():
        result = runner.invoke(validate_metadata_file, [file_path])
        assert result.exit_code == 0, f"Validation failed for {file_path}"

