# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
import shutil

import airbyte_lib as ab
import pandas as pd
import pytest
from airbyte_lib.caches import DuckDBCache, DuckDBCacheConfig, InMemoryCache, InMemoryCacheConfig, PostgresCache, PostgresCacheConfig
from airbyte_lib.sync_results import SyncResult


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


def test_sync_to_duckdb(expected_test_stream_data: dict[str, list[dict[str, str | int]]]):
    # source = ab.get_connector("source-test", config={"apiKey": "test"})
    # cache = ab.new_local_cache(
    #     source_catalog=source.configured_catalog,
    # )

    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = ab.new_local_cache(source_catalog=source.configured_catalog)

    result: SyncResult = source.read_all(cache)

    assert result.processed_records == 3
    for stream_name, expected_data in expected_test_stream_data.items():
        pd.testing.assert_frame_equal(
            result[stream_name].to_pandas(),
            pd.DataFrame(expected_data),
            check_dtype=False,
        )


def test_sync_to_postgres(new_pg_cache_config: PostgresCacheConfig, expected_test_stream_data: dict[str, list[dict[str, str | int]]]):
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = PostgresCache(
        config=new_pg_cache_config,
        source_catalog=source.configured_catalog,
    )

    result: SyncResult = source.read_all(cache)

    assert result.processed_records == 3
    for stream_name, expected_data in expected_test_stream_data.items():
        pd.testing.assert_frame_equal(
            result[stream_name].to_pandas(),
            pd.DataFrame(expected_data),
            check_dtype=False,
        )


@pytest.mark.skip(reason="InMemoryCache is not yet working.")
def test_sync_to_inmemory(expected_test_stream_data: dict[str, list[dict[str, str | int]]]):
    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = InMemoryCache(
        source_catalog=source.configured_catalog,
    )

    result: SyncResult = source.read_all(cache)

    assert result.processed_records == 3
    for stream_name, expected_data in expected_test_stream_data.items():
        pd.testing.assert_frame_equal(
            result[stream_name].to_pandas(),
            pd.DataFrame(expected_data),
            check_dtype=False,
        )


def test_sync_limited_streams(expected_test_stream_data):
    # source = ab.get_connector("source-test", config={"apiKey": "test"})
    # cache = ab.new_local_cache(source_catalog=source.configured_catalog)

    source = ab.get_connector("source-test", config={"apiKey": "test"})
    cache = ab.new_local_cache(source_catalog=source.configured_catalog)

    source.set_streams(["stream2"])

    result = source.read_all(cache)

    assert result.processed_records == 1
    pd.testing.assert_frame_equal(
        result["stream2"].to_pandas(),
        pd.DataFrame(expected_test_stream_data["stream2"]),
        check_dtype=False,
    )


def test_read_stream():
    source = ab.get_connector("source-test", config={"apiKey": "test"})

    assert list(source.get_stream_records("stream1")) == [{"column1": "value1", "column2": 1}, {"column1": "value2", "column2": 2}]


def test_read_stream_nonexisting():
    source = ab.get_connector("source-test", config={"apiKey": "test"})

    with pytest.raises(Exception):
        list(source.get_stream_records("non-existing"))

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
