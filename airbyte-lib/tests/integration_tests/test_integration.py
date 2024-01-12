# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
import shutil
from unittest.mock import Mock, call, patch

import airbyte_lib as ab
import pytest
from airbyte_lib.registry import _update_cache
from airbyte_lib.version import get_version


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
    os.environ["DO_NOT_TRACK"] = "true"

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


@pytest.mark.parametrize(
    "latest_available_version, requested_version, raises",
    [
        ("0.0.1", None, False),
        ("1.2.3", None, False),
        ("0.0.1", "latest", False),
        ("1.2.3", "latest", True),
        ("0.0.1", "0.0.1", False),
        ("1.2.3", "1.2.3", True),
    ])
def test_version_enforcement(raises, latest_available_version, requested_version):
    """"
    Ensures version enforcement works as expected:
    * If no version is specified, the current version is accepted
    * If the version is specified as "latest", only the latest available version is accepted
    * If the version is specified as a semantic version, only the exact version is accepted

    In this test, the actually installed version is 0.0.1
    """
    _update_cache()
    from airbyte_lib.registry import _cache
    _cache["source-test"].latest_available_version = latest_available_version
    if raises:
        with pytest.raises(Exception):
            ab.get_connector("source-test", version=requested_version, config={"apiKey": "abc"})
    else:
        ab.get_connector("source-test", version=requested_version, config={"apiKey": "abc"})

    # reset
    _cache["source-test"].latest_available_version = "0.0.1"


def test_check():
    source = ab.get_connector("source-test", config={"apiKey": "test"})

    source.check()


def test_check_fail():
    source = ab.get_connector("source-test", config={"apiKey": "wrong"})

    with pytest.raises(Exception):
        source.check()


@pytest.mark.parametrize(
    "method_call",
    [
        pytest.param(lambda source: source.check(), id="check"),
        pytest.param(lambda source: list(source.read_stream("stream1")), id="read_stream"),
        pytest.param(lambda source: source.read_all(), id="read_all"),
    ],
)
def test_check_fail_on_missing_config(method_call):
    source = ab.get_connector("source-test")

    with pytest.raises(Exception, match="Config is not set, either set in get_connector or via source.set_config"):
        method_call(source)


def test_sync():
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = ab.get_in_memory_cache()

    result = source.read_all(cache)

    assert result.processed_records == 3
    assert list(result["stream1"]) == [{"column1": "value1", "column2": 1}, {"column1": "value2", "column2": 2}]
    assert list(result["stream2"]) == [{"column1": "value1", "column2": 1}]

@patch('airbyte_lib.telemetry.requests')
@patch('airbyte_lib.telemetry.datetime')
@pytest.mark.parametrize(
    "raises, api_key, expected_state, expected_number_of_records",
    [
        (True, "test_fail_during_sync", "failed", 1),
        (False, "test", "succeeded", 3),
    ],
)
def test_tracking(mock_datetime: Mock, mock_requests: Mock, raises: bool, api_key: str, expected_state: str, expected_number_of_records: int):
    """
    Test that the telemetry is sent when the sync is successful.
    This is done by mocking the requests.post method and checking that it is called with the right arguments.
    """
    os.environ["DO_NOT_TRACK"] = ""

    now_date = Mock()
    mock_datetime.datetime = Mock()
    mock_datetime.datetime.utcnow.return_value = now_date
    now_date.isoformat.return_value = "2021-01-01T00:00:00.000000"

    mock_post = Mock()
    mock_requests.post = mock_post

    source = ab.get_connector("source-test", config={"apiKey": api_key})
    cache = ab.get_in_memory_cache()

    if raises:
        with pytest.raises(Exception):
            source.read_all(cache)
    else:
        source.read_all(cache)
    

    mock_post.assert_has_calls([
            call("https://api.segment.io/v1/track",
            auth=("jxT1qP9WEKwR3vtKMwP9qKhfQEGFtIM1", ""),
            json={
                "anonymousId": "airbyte-lib-user",
                "event": "sync",
                "properties": {
                    "version": get_version(),
                    "source": {'name': 'source-test', 'version': '0.0.1', 'type': 'venv'},
                    "state": "started",
                    "cache_type": "in_memory",
                    "ip": "0.0.0.0",
                },
                "timestamp": "2021-01-01T00:00:00.000000",
            }
        ),
    call(
            "https://api.segment.io/v1/track",
            auth=("jxT1qP9WEKwR3vtKMwP9qKhfQEGFtIM1", ""),
            json={
                "anonymousId": "airbyte-lib-user",
                "event": "sync",
                "properties": {
                    "version": get_version(),
                    "source": {'name': 'source-test', 'version': '0.0.1', 'type': 'venv'},
                    "state": expected_state,
                    "number_of_records": expected_number_of_records,
                    "cache_type": "in_memory",
                    "ip": "0.0.0.0",
                },
                "timestamp": "2021-01-01T00:00:00.000000",
            }
        )
    ])

    os.environ["DO_NOT_TRACK"] = "true"


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

def test_install_uninstall():
    source = ab.get_connector("source-test", pip_url="./tests/integration_tests/fixtures/source-test", config={"apiKey": "test"}, install_if_missing=False)

    source.uninstall()

    # assert that the venv is gone
    assert not os.path.exists(".venv-source-test")

    # assert that the connector is not available
    with pytest.raises(Exception):
        source.check()

    source.install()

    source.check()