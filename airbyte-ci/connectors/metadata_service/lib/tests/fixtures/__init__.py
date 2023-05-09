import pytest
import os
from typing import List


@pytest.fixture
def valid_metadata_yaml_files() -> List[str]:
    file_path = os.path.join(os.path.dirname(__file__), "valid")
    # list the absolute paths of all files in the directory
    return [os.path.join(file_path, file_name) for file_name in os.listdir(file_path)]


@pytest.fixture
def invalid_metadata_yaml_files() -> List[str]:
    file_path = os.path.join(os.path.dirname(__file__), "invalid")
    # list the absolute paths of all files in the directory
    return [os.path.join(file_path, file_name) for file_name in os.listdir(file_path)]
