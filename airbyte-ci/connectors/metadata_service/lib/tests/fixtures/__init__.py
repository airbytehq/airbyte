# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
from typing import Callable, List

import pytest
from metadata_service.constants import DOC_FILE_NAME


def list_all_paths_in_fixture_directory(folder_name: str) -> List[str]:
    file_path = os.path.join(os.path.dirname(__file__), folder_name)

    # If folder_name has subdirectories, os.walk will return a list of tuples,
    # one for folder_name and one for each of its subdirectories.
    fixture_files = []
    for root, dirs, files in os.walk(file_path):
        fixture_files.extend(os.path.join(root, file_name) for file_name in files)
    return fixture_files


@pytest.fixture(scope="session")
def valid_metadata_yaml_files() -> List[str]:
    files = list_all_paths_in_fixture_directory("metadata_validate/valid")
    if not files:
        pytest.fail("No files found in metadata_validate/valid")
    return files


@pytest.fixture(scope="session")
def invalid_metadata_yaml_files() -> List[str]:
    files = list_all_paths_in_fixture_directory("metadata_validate/invalid")
    if not files:
        pytest.fail("No files found in metadata_validate/invalid")
    return files


@pytest.fixture(scope="session")
def valid_metadata_upload_files() -> List[str]:
    files = list_all_paths_in_fixture_directory("metadata_upload/valid")
    if not files:
        pytest.fail("No files found in metadata_upload/valid")
    return files


@pytest.fixture(scope="session")
def invalid_metadata_upload_files() -> List[str]:
    files = list_all_paths_in_fixture_directory("metadata_upload/invalid")
    if not files:
        pytest.fail("No files found in metadata_upload/invalid")
    return files


@pytest.fixture(scope="session")
def get_fixture_path() -> Callable[[str], str]:
    def _get_fixture_path(fixture_name: str) -> str:
        return os.path.join(os.path.dirname(__file__), fixture_name)

    return _get_fixture_path
