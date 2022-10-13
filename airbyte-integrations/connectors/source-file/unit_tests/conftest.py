#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import pytest
from source_file.client import Client


@pytest.fixture
def read_file():
    def _read_file(file_name):
        parent_location = Path(__file__).absolute().parent
        file = open(parent_location / file_name).read()
        return file

    return _read_file


@pytest.fixture
def config():
    return {"dataset_name": "test", "format": "json", "url": "https://airbyte.com", "provider": {"storage": "HTTPS"}}


@pytest.fixture
def invalid_config(read_file):
    return {
        "dataset_name": "test",
        "format": "jsonl",
        "url": "https://airbyte.com",
        "reader_options": '{"encoding": "encoding"}',
        "provider": {"storage": "HTTPS"},
    }


@pytest.fixture
def client():
    return Client(
        dataset_name="test_dataset",
        url="scp://test_dataset",
        provider={"provider": {"storage": "HTTPS", "reader_impl": "gcsfs", "user_agent": True}},
    )


@pytest.fixture
def absolute_path():
    return Path(__file__).parent.absolute()


@pytest.fixture
def test_files():
    return "../integration_tests/sample_files"
