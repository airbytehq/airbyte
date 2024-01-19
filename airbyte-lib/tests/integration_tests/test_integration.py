# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
import shutil
from unittest.mock import Mock, call, patch
import tempfile
from pathlib import Path

import airbyte_lib as ab
import pandas as pd
import pytest

from airbyte_lib.caches import PostgresCache, PostgresCacheConfig
from airbyte_lib.registry import _update_cache
from airbyte_lib.version import get_version
from airbyte_lib.results import ReadResult


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

@pytest.fixture
def expected_test_stream_data() -> dict[str, list[dict[str, str | int]]]:
    return {
        "stream1": [
            {"column1": "value1", "column2": 1},
            {"column1": "value2", "column2": 2},
        ],
        "stream2": [
            {"column1": "value1", "column2": 1},
        ],
    }

def test_list_streams(expected_test_stream_data: dict[str, list[dict[str, str | int]]]):
    source = ab.get_connector("source-test", config={"apiKey": "test"})

    assert source.get_available_streams() == list(expected_test_stream_data.keys())


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


def test_file_write_and_cleanup() -> None:
    """Ensure files are written to the correct location and cleaned up afterwards."""
    with tempfile.TemporaryDirectory() as temp_dir_1, tempfile.TemporaryDirectory() as temp_dir_2:
        cache_w_cleanup = ab.new_local_cache(cache_dir=temp_dir_1, cleanup=True)
        cache_wo_cleanup = ab.new_local_cache(cache_dir=temp_dir_2, cleanup=False)

        source = ab.get_connector("source-test", config={"apiKey": "test"})

        _ = source.read(cache_w_cleanup)
        _ = source.read(cache_wo_cleanup)

        assert len(list(Path(temp_dir_1).glob("*.parquet"))) == 0, "Expected files to be cleaned up"
        assert len(list(Path(temp_dir_2).glob("*.parquet"))) == 2, "Expected files to exist"


def test_sync_to_duckdb(expected_test_stream_data: dict[str, list[dict[str, str | int]]]):
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = ab.new_local_cache()

    result: ReadResult = source.read(cache)

    assert result.processed_records == 3
    for stream_name, expected_data in expected_test_stream_data.items():
        pd.testing.assert_frame_equal(
            result[stream_name].to_pandas(),
            pd.DataFrame(expected_data),
            check_dtype=False,
        )


def test_read_result_as_list(expected_test_stream_data: dict[str, list[dict[str, str | int]]]):
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = ab.new_local_cache()

    result: ReadResult = source.read(cache)
    stream_1_list = list(result["stream1"])
    stream_2_list = list(result["stream2"])
    assert stream_1_list == expected_test_stream_data["stream1"]
    assert stream_2_list == expected_test_stream_data["stream2"]


def test_get_records_result_as_list(expected_test_stream_data: dict[str, list[dict[str, str | int]]]):
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = ab.new_local_cache()

    stream_1_list = list(source.get_records("stream1"))
    stream_2_list = list(source.get_records("stream2"))
    assert stream_1_list == expected_test_stream_data["stream1"]
    assert stream_2_list == expected_test_stream_data["stream2"]



def test_sync_with_merge_to_duckdb(expected_test_stream_data: dict[str, list[dict[str, str | int]]]):
    """Test that the merge strategy works as expected.

    In this test, we sync the same data twice. If the data is not duplicated, we assume
    the merge was successful.

    # TODO: Add a check with a primary key to ensure that the merge strategy works as expected.
    """
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = ab.new_local_cache()

    # Read twice to test merge strategy
    result: ReadResult = source.read(cache)
    result: ReadResult = source.read(cache)

    assert result.processed_records == 3
    for stream_name, expected_data in expected_test_stream_data.items():
        pd.testing.assert_frame_equal(
            result[stream_name].to_pandas(),
            pd.DataFrame(expected_data),
            check_dtype=False,
        )


@pytest.mark.parametrize(
    "method_call",
    [
        pytest.param(lambda source: source.check(), id="check"),
        pytest.param(lambda source: list(source.get_records("stream1")), id="read_stream"),
        pytest.param(lambda source: source.read(), id="read"),
    ],
)
def test_check_fail_on_missing_config(method_call):
    source = ab.get_connector("source-test")

    with pytest.raises(Exception, match="Config is not set, either set in get_connector or via source.set_config"):
        method_call(source)

def test_sync_with_merge_to_postgres(new_pg_cache_config: PostgresCacheConfig, expected_test_stream_data: dict[str, list[dict[str, str | int]]]):
    """Test that the merge strategy works as expected.

    In this test, we sync the same data twice. If the data is not duplicated, we assume
    the merge was successful.

    # TODO: Add a check with a primary key to ensure that the merge strategy works as expected.
    """
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = PostgresCache(config=new_pg_cache_config)

    # Read twice to test merge strategy
    result: ReadResult = source.read(cache)
    result: ReadResult = source.read(cache)

    assert result.processed_records == 3
    for stream_name, expected_data in expected_test_stream_data.items():
        pd.testing.assert_frame_equal(
            result[stream_name].to_pandas(),
            pd.DataFrame(expected_data),
            check_dtype=False,
        )

@patch.dict('os.environ', {'DO_NOT_TRACK': ''})
@patch('airbyte_lib.telemetry.requests')
@patch('airbyte_lib.telemetry.datetime')
@pytest.mark.parametrize(
    "raises, api_key, expected_state, expected_number_of_records, request_call_fails, extra_env, expected_flags",
    [
        pytest.param(True, "test_fail_during_sync", "failed", 1, False, {}, {"CI": False}, id="fail_during_sync"),
        pytest.param(False, "test", "succeeded", 3, False, {}, {"CI": False}, id="succeed_during_sync"),
        pytest.param(False, "test", "succeeded", 3, True, {}, {"CI": False}, id="fail_request_without_propagating"),
        pytest.param(False, "test", "succeeded", 3, False, {"CI": ""}, {"CI": False}, id="falsy_ci_flag"),
        pytest.param(False, "test", "succeeded", 3, False, {"CI": "true"}, {"CI": True}, id="truthy_ci_flag"),
    ],
)
def test_tracking(mock_datetime: Mock, mock_requests: Mock, raises: bool, api_key: str, expected_state: str, expected_number_of_records: int, request_call_fails: bool, extra_env: dict[str, str], expected_flags: dict[str, bool]):
    """
    Test that the telemetry is sent when the sync is successful.
    This is done by mocking the requests.post method and checking that it is called with the right arguments.
    """
    now_date = Mock()
    mock_datetime.datetime = Mock()
    mock_datetime.datetime.utcnow.return_value = now_date
    now_date.isoformat.return_value = "2021-01-01T00:00:00.000000"

    mock_post = Mock()
    mock_requests.post = mock_post

    source = ab.get_connector("source-test", config={"apiKey": api_key})
    cache = ab.get_default_cache()

    if request_call_fails:
        mock_post.side_effect = Exception("test exception")

    with patch.dict('os.environ', extra_env):
        if raises:
            with pytest.raises(Exception):
                source.read(cache)
        else:
            source.read(cache)
    

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
                    "cache": {"type": "duckdb"},
                    "ip": "0.0.0.0",
                    "flags": expected_flags
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
                    "cache": {"type": "duckdb"},
                    "ip": "0.0.0.0",
                    "flags": expected_flags
                },
                "timestamp": "2021-01-01T00:00:00.000000",
            }
        )
    ])


def test_sync_to_postgres(new_pg_cache_config: PostgresCacheConfig, expected_test_stream_data: dict[str, list[dict[str, str | int]]]):
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = PostgresCache(config=new_pg_cache_config)

    result: ReadResult = source.read(cache)

    assert result.processed_records == 3
    for stream_name, expected_data in expected_test_stream_data.items():
        pd.testing.assert_frame_equal(
            result[stream_name].to_pandas(),
            pd.DataFrame(expected_data),
            check_dtype=False,
        )


def test_sync_limited_streams(expected_test_stream_data):
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = ab.new_local_cache()

    source.set_streams(["stream2"])

    result = source.read(cache)

    assert result.processed_records == 1
    pd.testing.assert_frame_equal(
        result["stream2"].to_pandas(),
        pd.DataFrame(expected_test_stream_data["stream2"]),
        check_dtype=False,
    )


def test_read_stream():
    source = ab.get_connector("source-test", config={"apiKey": "test"})

    assert list(source.get_records("stream1")) == [{"column1": "value1", "column2": 1}, {"column1": "value2", "column2": 2}]


def test_read_stream_nonexisting():
    source = ab.get_connector("source-test", config={"apiKey": "test"})

    with pytest.raises(Exception):
        list(source.get_records("non-existing"))

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