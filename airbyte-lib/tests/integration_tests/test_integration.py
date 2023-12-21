# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
import shutil

import airbyte_lib as ab
import pytest


@pytest.fixture(scope="module", autouse=True)
def prepare_test_env():
    """
    Prepare test environment. This will pre-install the test source from the fixtures array and set the environment variable to use the local json file as registry.
    """
    if os.path.exists(".venv-source-test"):
        shutil.rmtree(".venv-source-test")

    os.system("python -m venv .venv-source-test")
    os.system("source .venv-source-test/bin/activate && pip install -e ./tests/integration_tests/fixtures/source-test")
    os.environ["AIRBYTE_LOCAL_REGISTRY"] = "./tests/integration_tests/fixtures/registry.json"

    yield

    shutil.rmtree(".venv-source-test")


def test_list_streams():
    source = ab.get_connector("source-test", config={"apiKey": "test"})

    assert source.get_available_streams() == ["stream1", "stream2"]


def test_invalid_config():
    with pytest.raises(Exception):
        ab.get_connector("source-test", config={"apiKey": 1234})


def test_non_existing_connector():
    with pytest.raises(Exception):
        ab.get_connector("source-not-existing", config={"apiKey": "abc"})


def test_wrong_version():
    with pytest.raises(Exception):
        ab.get_connector("source-test", version="1.2.3", config={"apiKey": "abc"})


def test_check():
    source = ab.get_connector("source-test", config={"apiKey": "test"})

    source.check()


def test_check_fail():
    source = ab.get_connector("source-test", config={"apiKey": "wrong"})

    with pytest.raises(Exception):
        source.check()


def test_sync():
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = ab.get_in_memory_cache()

    result = source.read_all(cache)

    assert result.processed_records == 3
    assert list(result["stream1"]) == [{"column1": "value1", "column2": 1}, {"column1": "value2", "column2": 2}]
    assert list(result["stream2"]) == [{"column1": "value1", "column2": 1}]


def test_sync_limited_streams():
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = ab.get_in_memory_cache()

    source.set_streams(["stream2"])

    result = source.read_all(cache)

    assert result.processed_records == 1
    assert list(result["stream2"]) == [{"column1": "value1", "column2": 1}]


def test_read_stream():
    source = ab.get_connector("source-test", config={"apiKey": "test"})

    assert list(source.read_stream("stream1")) == [{"column1": "value1", "column2": 1}, {"column1": "value2", "column2": 2}]


def test_read_stream_nonexisting():
    source = ab.get_connector("source-test", config={"apiKey": "test"})

    with pytest.raises(Exception):
        list(source.read_stream("non-existing"))

def test_failing_path_connector():
    with pytest.raises(Exception):
        ab.get_connector("source-test", config={"apiKey": "test"}, use_local_install=True)

def test_succeeding_path_connector():
    old_path = os.environ["PATH"]

    # set path to include the test venv bin folder
    os.environ["PATH"] = f"{os.path.abspath('.venv-source-test/bin')}:{os.environ['PATH']}"
    source = ab.get_connector("source-test", config={"apiKey": "test"}, use_local_install=True)
    source.check()

    os.environ["PATH"] = old_path
