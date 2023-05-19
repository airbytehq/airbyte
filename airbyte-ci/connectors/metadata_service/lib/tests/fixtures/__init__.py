import pytest
import os
from typing import List


def list_all_paths_in_fixture_directory(folder_name: str) -> List[str]:
    return Path( os.path.dirname(__file__) / folder_name).iterdir()


@pytest.fixture
def valid_metadata_yaml_files() -> List[str]:
    return list_all_paths_in_fixture_directory("metadata_validate/valid")


@pytest.fixture
def invalid_metadata_yaml_files() -> List[str]:
    return list_all_paths_in_fixture_directory("metadata_validate/invalid")


@pytest.fixture(scope="session")
def valid_metadata_upload_files() -> List[str]:
    return list_all_paths_in_fixture_directory("metadata_upload/valid")


@pytest.fixture
def invalid_metadata_upload_files() -> List[str]:
    return list_all_paths_in_fixture_directory("metadata_upload/invalid")
