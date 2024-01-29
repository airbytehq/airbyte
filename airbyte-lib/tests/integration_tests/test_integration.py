# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from collections.abc import Mapping
import os
import shutil
from typing import Any
from unittest.mock import Mock, call, patch
import tempfile
from pathlib import Path
from airbyte_lib.caches.base import SQLCacheBase

from sqlalchemy import column, text

import airbyte_lib as ab
from airbyte_lib.caches import SnowflakeCacheConfig, SnowflakeSQLCache
import pandas as pd
import pytest

from airbyte_lib.caches import PostgresCache, PostgresCacheConfig
from airbyte_lib.registry import _update_cache
from airbyte_lib.version import get_version
from airbyte_lib.results import ReadResult
from airbyte_lib.datasets import CachedDataset, LazyDataset, SQLDataset
import airbyte_lib as ab

from airbyte_lib.results import ReadResult
from airbyte_lib import exceptions as exc
import ulid


@pytest.fixture(scope="module", autouse=True)
def prepare_test_env():
    """
    Prepare test environment. This will pre-install the test source from the fixtures array and set the environment variable to use the local json file as registry.
    """
    if os.path.exists(".venv-source-test"):
        shutil.rmtree(".venv-source-test")

    os.system("python -m venv .venv-source-test")
    os.system(".venv-source-test/bin/pip install -e ./tests/integration_tests/fixtures/source-test")

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


def assert_cache_data(expected_test_stream_data: dict[str, list[dict[str, str | int]]], cache: SQLCacheBase, streams: list[str] = None):
    for stream_name in streams or expected_test_stream_data.keys():
        pd.testing.assert_frame_equal(
            cache[stream_name].to_pandas(),
            pd.DataFrame(expected_test_stream_data[stream_name]),
            check_dtype=False,
        )
    
    # validate that the cache doesn't contain any other streams
    if streams:
        assert len(list(cache.__iter__())) == len(streams)


def test_sync_to_duckdb(expected_test_stream_data: dict[str, list[dict[str, str | int]]]):
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = ab.new_local_cache()

    result: ReadResult = source.read(cache)

    assert result.processed_records == 3
    assert_cache_data(expected_test_stream_data, cache)


def test_read_from_cache(expected_test_stream_data: dict[str, list[dict[str, str | int]]]):
    """
    Test that we can read from a cache that already has data (identigier by name)
    """
    cache_name = str(ulid.ULID())
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = ab.new_local_cache(cache_name)

    source.read(cache)

    # Create a new cache pointing to the same duckdb file
    second_cache = ab.new_local_cache(cache_name)


    assert_cache_data(expected_test_stream_data, second_cache)


def test_read_isolated_by_prefix(expected_test_stream_data: dict[str, list[dict[str, str | int]]]):
    """
    Test that cache correctly isolates streams when different table prefixes are used
    """
    cache_name = str(ulid.ULID())
    db_path = Path(f"./.cache/{cache_name}.duckdb")
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = ab.DuckDBCache(config=ab.DuckDBCacheConfig(db_path=db_path, table_prefix="prefix_"))

    source.read(cache)

    same_prefix_cache = ab.DuckDBCache(config=ab.DuckDBCacheConfig(db_path=db_path, table_prefix="prefix_"))
    different_prefix_cache = ab.DuckDBCache(config=ab.DuckDBCacheConfig(db_path=db_path, table_prefix="different_prefix_"))
    no_prefix_cache = ab.DuckDBCache(config=ab.DuckDBCacheConfig(db_path=db_path, table_prefix=None))

    # validate that the cache with the same prefix has the data as expected, while the other two are empty
    assert_cache_data(expected_test_stream_data, same_prefix_cache)
    assert len(list(different_prefix_cache.__iter__())) == 0
    assert len(list(no_prefix_cache.__iter__())) == 0

    # read partial data into the other two caches
    source.set_streams(["stream1"])
    source.read(different_prefix_cache)
    source.read(no_prefix_cache)

    second_same_prefix_cache = ab.DuckDBCache(config=ab.DuckDBCacheConfig(db_path=db_path, table_prefix="prefix_"))
    second_different_prefix_cache = ab.DuckDBCache(config=ab.DuckDBCacheConfig(db_path=db_path, table_prefix="different_prefix_"))
    second_no_prefix_cache = ab.DuckDBCache(config=ab.DuckDBCacheConfig(db_path=db_path, table_prefix=None))

    # validate that the first cache still has full data, while the other two have partial data
    assert_cache_data(expected_test_stream_data, second_same_prefix_cache)
    assert_cache_data(expected_test_stream_data, second_different_prefix_cache, streams=["stream1"])
    assert_cache_data(expected_test_stream_data, second_no_prefix_cache, streams=["stream1"])


def test_merge_streams_in_cache(expected_test_stream_data: dict[str, list[dict[str, str | int]]]):
    """
    Test that we can extend a cache with new streams
    """
    cache_name = str(ulid.ULID())
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = ab.new_local_cache(cache_name)

    source.set_streams(["stream1"])
    source.read(cache)

    # Assert that the cache only contains stream1
    with pytest.raises(KeyError):
        cache["stream2"]

    # Create a new cache with the same name
    second_cache = ab.new_local_cache(cache_name)
    source.set_streams(["stream2"])
    result = source.read(second_cache)

    # Assert that the read result only contains stream2
    with pytest.raises(KeyError):
        result["stream1"]

    assert_cache_data(expected_test_stream_data, second_cache)


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


def test_cached_dataset(
    expected_test_stream_data: dict[str, list[dict[str, str | int]]],
) -> None:
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    result: ReadResult = source.read(ab.new_local_cache())

    stream_name = "stream1"
    not_a_stream_name = "not_a_stream"

    # Check that the stream appears in mapping-like attributes
    assert stream_name in result.cache._streams_with_data
    assert stream_name in result
    assert stream_name in result.cache
    assert stream_name in result.cache.streams
    assert stream_name in result.streams

    stream_get_a: CachedDataset = result[stream_name]
    stream_get_b: CachedDataset = result.streams[stream_name]
    stream_get_c: CachedDataset = result.cache[stream_name]
    stream_get_d: CachedDataset = result.cache.streams[stream_name]

    # Check that each get method is syntactically equivalent

    assert isinstance(stream_get_a, CachedDataset)
    assert isinstance(stream_get_b, CachedDataset)
    assert isinstance(stream_get_c, CachedDataset)
    assert isinstance(stream_get_d, CachedDataset)

    assert stream_get_a == stream_get_b
    assert stream_get_b == stream_get_c
    assert stream_get_c == stream_get_d

    # Check that we can iterate over the stream

    list_from_iter_a = list(stream_get_a)
    list_from_iter_b = [row for row in stream_get_a]

    # Make sure that we get a key error if we try to access a stream that doesn't exist
    with pytest.raises(KeyError):
        result[not_a_stream_name]
    with pytest.raises(KeyError):
        result.streams[not_a_stream_name]
    with pytest.raises(KeyError):
        result.cache[not_a_stream_name]
    with pytest.raises(KeyError):
        result.cache.streams[not_a_stream_name]

    # Make sure we can use "result.streams.items()"
    for stream_name, cached_dataset in result.streams.items():
        assert isinstance(cached_dataset, CachedDataset)
        assert isinstance(stream_name, str)

        list_data = list(cached_dataset)
        assert list_data == expected_test_stream_data[stream_name]

    # Make sure we can use "result.cache.streams.items()"
    for stream_name, cached_dataset in result.cache.streams.items():
        assert isinstance(cached_dataset, CachedDataset)
        assert isinstance(stream_name, str)

        list_data = list(cached_dataset)
        assert list_data == expected_test_stream_data[stream_name]


def test_cached_dataset_filter():
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    result: ReadResult = source.read(ab.new_local_cache())

    stream_name = "stream1"

    # Check the many ways to add a filter:
    cached_dataset: CachedDataset = result[stream_name]
    filtered_dataset_a: SQLDataset = cached_dataset.with_filter("column2 == 1")
    filtered_dataset_b: SQLDataset = cached_dataset.with_filter(text("column2 == 1"))
    filtered_dataset_c: SQLDataset = cached_dataset.with_filter(column("column2") == 1)

    assert isinstance(cached_dataset, CachedDataset)
    all_records = list(cached_dataset)
    assert len(all_records) == 2

    for filtered_dataset, case in [
        (filtered_dataset_a, "a"),
        (filtered_dataset_b, "b"),
        (filtered_dataset_c, "c"),
    ]:
        assert isinstance(filtered_dataset, SQLDataset)

        # Check that we can iterate over each stream

        filtered_records: list[Mapping[str, Any]] = [row for row in filtered_dataset]

        # Check that the filter worked
        assert len(filtered_records) == 1, f"Case '{case}' had incorrect number of records."

        # Assert the stream name still matches
        assert filtered_dataset.stream_name == stream_name, \
            f"Case '{case}' had incorrect stream name."

        # Check that chaining filters works
        chained_dataset = filtered_dataset.with_filter("column1 == 'value1'")
        chained_records = [row for row in chained_dataset]
        assert len(chained_records) == 1, \
            f"Case '{case}' had incorrect number of records after chaining filters."


def test_lazy_dataset_from_source(
    expected_test_stream_data: dict[str, list[dict[str, str | int]]],
) -> None:
    source = ab.get_connector("source-test", config={"apiKey": "test"})

    stream_name = "stream1"
    not_a_stream_name = "not_a_stream"

    lazy_dataset_a = source.get_records(stream_name)
    lazy_dataset_b = source.get_records(stream_name)

    assert isinstance(lazy_dataset_a, LazyDataset)

    # Check that we can iterate over the stream

    list_from_iter_a = list(lazy_dataset_a)
    list_from_iter_b = [row for row in lazy_dataset_b]

    assert list_from_iter_a == list_from_iter_b

    # Make sure that we get a key error if we try to access a stream that doesn't exist
    with pytest.raises(exc.AirbyteLibInputError):
        source.get_records(not_a_stream_name)

    # Make sure we can iterate on all available streams
    for stream_name in source.get_available_streams():
        assert isinstance(stream_name, str)

        lazy_dataset: LazyDataset = source.get_records(stream_name)
        assert isinstance(lazy_dataset, LazyDataset)

        list_data = list(lazy_dataset)
        assert list_data == expected_test_stream_data[stream_name]


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

    with pytest.raises(exc.AirbyteConnectorConfigurationMissingError):
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
        pytest.param(True, "test_fail_during_sync", "failed", 1, False, {"CI": ""}, {"CI": False}, id="fail_during_sync"),
        pytest.param(False, "test", "succeeded", 3, False, {"CI": ""}, {"CI": False}, id="succeed_during_sync"),
        pytest.param(False, "test", "succeeded", 3, True, {"CI": ""}, {"CI": False}, id="fail_request_without_propagating"),
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

def test_sync_to_snowflake(snowflake_config: SnowflakeCacheConfig, expected_test_stream_data: dict[str, list[dict[str, str | int]]]):
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = SnowflakeSQLCache(config=snowflake_config)

    with cache.get_sql_connection() as con:
        con.execute("DROP SCHEMA IF EXISTS AIRBYTE_RAW")

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
