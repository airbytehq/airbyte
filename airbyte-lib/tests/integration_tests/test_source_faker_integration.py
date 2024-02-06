# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""Integration tests which leverage the source-faker connector to test the framework end-to-end.

Since source-faker is included in dev dependencies, we can assume `source-faker` is installed
and available on PATH for the poetry-managed venv.
"""
from __future__ import annotations
from collections.abc import Generator
import os
import sys
import shutil
from pathlib import Path

import pytest

import airbyte_lib as ab
from airbyte_lib import caches
from airbyte_cdk.models import ConfiguredAirbyteCatalog
import ulid


# Product count is always the same, regardless of faker scale.
NUM_PRODUCTS = 100

SEED_A = 1234
SEED_B = 5678

# Number of records in each of the 'users' and 'purchases' streams.
FAKER_SCALE_A = 200
# We want this to be different from FAKER_SCALE_A.
FAKER_SCALE_B = 300


# Patch PATH to include the source-faker executable.

@pytest.fixture(autouse=True)
def add_venv_bin_to_path(monkeypatch):
    # Get the path to the bin directory of the virtual environment
    venv_bin_path = os.path.join(sys.prefix, 'bin')

    # Add the bin directory to the PATH
    new_path = f"{venv_bin_path}:{os.environ['PATH']}"
    monkeypatch.setenv('PATH', new_path)


def test_which_source_faker() -> None:
    """Test that source-faker is available on PATH."""
    assert shutil.which("source-faker") is not None, \
        f"Can't find source-faker on PATH: {os.environ['PATH']}"


@pytest.fixture(scope="function")  # Each test gets a fresh source-faker instance.
def source_faker_seed_a() -> ab.Source:
    """Fixture to return a source-faker connector instance."""
    source = ab.get_source(
        "source-faker",
        local_executable="source-faker",
        config={
            "count": FAKER_SCALE_A,
            "seed": SEED_A,
            "parallelism": 16,  # Otherwise defaults to 4.
        },
        install_if_missing=False,  # Should already be on PATH
    )
    source.check()
    # TODO: We can optionally add back 'users' once Postgres can handle complex object types.
    source.set_streams([
        "products",
        "purchases",
    ])
    return source


@pytest.fixture(scope="function")  # Each test gets a fresh source-faker instance.
def source_faker_seed_b() -> ab.Source:
    """Fixture to return a source-faker connector instance."""
    source = ab.get_source(
        "source-faker",
        local_executable="source-faker",
        config={
            "count": FAKER_SCALE_B,
            "seed": SEED_B,
            "parallelism": 16,  # Otherwise defaults to 4.
        },
        install_if_missing=False,  # Should already be on PATH
    )
    source.check()
    # TODO: We can optionally add back 'users' once Postgres can handle complex object types.
    source.set_streams([
        "products",
        "purchases",
    ])
    return source


@pytest.fixture(scope="function")
def duckdb_cache() -> Generator[caches.DuckDBCache, None, None]:
    """Fixture to return a fresh cache."""
    cache: caches.DuckDBCache = ab.new_local_cache()
    yield cache
    # TODO: Delete cache DB file after test is complete.
    return


@pytest.fixture(scope="function")
def snowflake_cache(snowflake_config) -> Generator[caches.SnowflakeCache, None, None]:
    """Fixture to return a fresh cache."""
    cache: caches.SnowflakeCache = caches.SnowflakeSQLCache(snowflake_config)
    yield cache
    # TODO: Delete cache DB file after test is complete.
    return


@pytest.fixture(scope="function")
def postgres_cache(new_pg_cache_config) -> Generator[caches.PostgresCache, None, None]:
    """Fixture to return a fresh cache."""
    cache: caches.PostgresCache = caches.PostgresCache(config=new_pg_cache_config)
    yield cache
    # TODO: Delete cache DB file after test is complete.
    return


@pytest.fixture
def all_cache_types(
    duckdb_cache: ab.DuckDBCache,
    snowflake_cache: ab.SnowflakeCache,
    postgres_cache: ab.PostgresCache,
):
    _ = postgres_cache
    return [
        duckdb_cache,
        postgres_cache,
        # snowflake_cache,  # Snowflake works, but is slow and expensive to test. # TODO: Re-enable.
    ]


def test_faker_pks(
    source_faker_seed_a: ab.Source,
    duckdb_cache: ab.DuckDBCache,
) -> None:
    """Test that the append strategy works as expected."""

    catalog: ConfiguredAirbyteCatalog = source_faker_seed_a.configured_catalog

    assert len(catalog.streams) == 2
    assert catalog.streams[0].primary_key
    assert catalog.streams[1].primary_key

    read_result = source_faker_seed_a.read(duckdb_cache, write_strategy="append")
    assert read_result.cache._get_primary_keys("products") == ["id"]
    assert read_result.cache._get_primary_keys("purchases") == ["id"]


def test_replace_strategy(
    source_faker_seed_a: ab.Source,
    all_cache_types: ab.DuckDBCache,
) -> None:
    """Test that the append strategy works as expected."""
    for cache in all_cache_types: # Function-scoped fixtures can't be used in parametrized().
        for _ in range(2):
            result = source_faker_seed_a.read(
                cache, write_strategy="replace", force_full_refresh=True
            )
            assert len(result.cache.streams) == 2
            assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS
            assert len(list(result.cache.streams["purchases"])) == FAKER_SCALE_A


def test_append_strategy(
    source_faker_seed_a: ab.Source,
    all_cache_types: ab.DuckDBCache,
) -> None:
    """Test that the append strategy works as expected."""
    for cache in all_cache_types: # Function-scoped fixtures can't be used in parametrized().
        for iteration in range(1, 3):
            result = source_faker_seed_a.read(cache, write_strategy="append")
            assert len(result.cache.streams) == 2
            assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS * iteration
            assert len(list(result.cache.streams["purchases"])) == FAKER_SCALE_A * iteration


@pytest.mark.parametrize("strategy", ["merge", "auto"])
def test_merge_strategy(
    strategy: str,
    source_faker_seed_a: ab.Source,
    source_faker_seed_b: ab.Source,
    all_cache_types: ab.DuckDBCache,
) -> None:
    """Test that the merge strategy works as expected.

    Since all streams have primary keys, we should expect the auto strategy to be identical to the
    merge strategy.
    """
    for cache in all_cache_types: # Function-scoped fixtures can't be used in parametrized().
        # First run, seed A (counts should match the scale or the product count)
        result = source_faker_seed_a.read(cache, write_strategy=strategy)
        assert len(result.cache.streams) == 2
        assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS
        assert len(list(result.cache.streams["purchases"])) == FAKER_SCALE_A

        # Second run, also seed A (should have same exact data, no change in counts)
        result = source_faker_seed_a.read(cache, write_strategy=strategy)
        assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS
        assert len(list(result.cache.streams["purchases"])) == FAKER_SCALE_A

        # Third run, seed B - should increase record count to the scale of B, which is greater than A.
        # TODO: See if we can reliably predict the exact number of records, since we use fixed seeds.
        result = source_faker_seed_b.read(cache, write_strategy=strategy)
        assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS
        assert len(list(result.cache.streams["purchases"])) == FAKER_SCALE_B

        # Third run, seed A again - count should stay at scale B, since A is smaller.
        # TODO: See if we can reliably predict the exact number of records, since we use fixed seeds.
        result = source_faker_seed_a.read(cache, write_strategy=strategy)
        assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS
        assert len(list(result.cache.streams["purchases"])) == FAKER_SCALE_B


def test_incremental_sync(
    source_faker_seed_a: ab.Source,
    source_faker_seed_b: ab.Source,
    duckdb_cache: ab.DuckDBCache,
) -> None:
    config_a = source_faker_seed_a.get_config()
    config_b = source_faker_seed_b.get_config()
    config_a["always_updated"] = False
    config_b["always_updated"] = False
    source_faker_seed_a.set_config(config_a)
    source_faker_seed_b.set_config(config_b)

    result1 = source_faker_seed_a.read(duckdb_cache)
    assert len(list(result1.cache.streams["products"])) == NUM_PRODUCTS
    assert len(list(result1.cache.streams["purchases"])) == FAKER_SCALE_A
    assert result1.processed_records == NUM_PRODUCTS + FAKER_SCALE_A

    assert not duckdb_cache.get_state() == [] 

    # Second run should not return records as it picks up the state and knows it's up to date.
    result2 = source_faker_seed_b.read(duckdb_cache)

    assert result2.processed_records == 0
    assert len(list(result2.cache.streams["products"])) == NUM_PRODUCTS
    assert len(list(result2.cache.streams["purchases"])) == FAKER_SCALE_A


def test_incremental_state_cache_persistence(
    source_faker_seed_a: ab.Source,
    source_faker_seed_b: ab.Source,
) -> None:
    config_a = source_faker_seed_a.get_config()
    config_b = source_faker_seed_b.get_config()
    config_a["always_updated"] = False
    config_b["always_updated"] = False
    source_faker_seed_a.set_config(config_a)
    source_faker_seed_b.set_config(config_b)
    cache_name = str(ulid.ULID())
    cache = ab.new_local_cache(cache_name)
    result = source_faker_seed_a.read(cache)
    assert result.processed_records == NUM_PRODUCTS + FAKER_SCALE_A
    second_cache = ab.new_local_cache(cache_name)
    # The state should be persisted across cache instances.
    result2 = source_faker_seed_b.read(second_cache)
    assert result2.processed_records == 0

    assert not second_cache.get_state() == [] 
    assert len(list(result2.cache.streams["products"])) == NUM_PRODUCTS
    assert len(list(result2.cache.streams["purchases"])) == FAKER_SCALE_A


def test_incremental_state_prefix_isolation(
    source_faker_seed_a: ab.Source,
    source_faker_seed_b: ab.Source,
) -> None:
    """
    Test that state in the cache correctly isolates streams when different table prefixes are used
    """
    config_a = source_faker_seed_a.get_config()
    config_a["always_updated"] = False
    source_faker_seed_a.set_config(config_a)
    cache_name = str(ulid.ULID())
    db_path = Path(f"./.cache/{cache_name}.duckdb")
    cache = ab.DuckDBCache(config=ab.DuckDBCacheConfig(db_path=db_path, table_prefix="prefix_"))
    different_prefix_cache = ab.DuckDBCache(config=ab.DuckDBCacheConfig(db_path=db_path, table_prefix="different_prefix_"))

    result = source_faker_seed_a.read(cache)
    assert result.processed_records == NUM_PRODUCTS + FAKER_SCALE_A

    result2 = source_faker_seed_b.read(different_prefix_cache)
    assert result2.processed_records == NUM_PRODUCTS + FAKER_SCALE_B

    assert len(list(result2.cache.streams["products"])) == NUM_PRODUCTS
    assert len(list(result2.cache.streams["purchases"])) == FAKER_SCALE_B