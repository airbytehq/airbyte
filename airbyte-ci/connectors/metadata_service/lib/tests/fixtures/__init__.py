import os
from typing import Callable, List

import pytest
from metadata_service.constants import DOC_FILE_NAME


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


@pytest.fixture(scope="session")
def get_fixture_path() -> Callable[[str], str]:
    def _get_fixture_path(fixture_name: str) -> str:
        return os.path.join(os.path.dirname(__file__), fixture_name)

    return _get_fixture_path
