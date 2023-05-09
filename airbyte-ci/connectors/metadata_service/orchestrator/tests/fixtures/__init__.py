import json
import pytest
import os


@pytest.fixture
def oss_catalog_dict():
    file_path = os.path.join(os.path.dirname(__file__), "oss_catalog.json")
    return json.load(open(file_path))


@pytest.fixture
def cloud_catalog_dict():
    file_path = os.path.join(os.path.dirname(__file__), "cloud_catalog.json")
    return json.load(open(file_path))
