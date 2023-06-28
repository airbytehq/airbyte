import pytest
import os
from typing import List


def list_all_paths_in_fixture_directory(folder_name: str) -> List[str]:
    file_path = os.path.join(os.path.dirname(__file__), folder_name)
    for root, dirs, files in os.walk(file_path):
        return [os.path.join(root, file_name) for file_name in files]

@pytest.fixture(scope="session")
def valid_metadata_yaml_files() -> List[str]:
    return list_all_paths_in_fixture_directory("metadata_validate/valid")


@pytest.fixture(scope="session")
def invalid_metadata_yaml_files() -> List[str]:
    return list_all_paths_in_fixture_directory("metadata_validate/invalid")


@pytest.fixture(scope="session")
def valid_metadata_upload_files() -> List[str]:
    return list_all_paths_in_fixture_directory("metadata_upload/valid")


@pytest.fixture(scope="session")
def invalid_metadata_upload_files() -> List[str]:
    return list_all_paths_in_fixture_directory("metadata_upload/invalid")
