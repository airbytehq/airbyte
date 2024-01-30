"""Integration tests which leverage the source-faker connector to test the framework end-to-end.

Since source-faker is included in dev dependencies, we can assume `source-faker` is installed
and available on PATH for the poetry-managed venv.
"""
from __future__ import annotations
from collections.abc import Generator

import pytest

import airbyte_lib as ab
from airbyte_cdk.models import ConfiguredAirbyteCatalog


# Product count is always the same, regardless of faker scale.
NUM_PRODUCTS = 100

SEED_A = 1234
SEED_B = 5678

# Number of records in each of the 'users' and 'purchases' streams.
FAKER_SCALE_A = 500
# We want this to be different from FAKER_SCALE_A.
FAKER_SCALE_B = 600


@pytest.fixture(scope="function")  # Each test gets a fresh source-faker instance.
def source_faker_seed_a():
    """Fixture to return a source-faker connector instance."""
    source = ab.get_connector(
        "source-faker",
        config={
            "count": FAKER_SCALE_A,
            "seed": SEED_A,
            "parallelism": 16,  # Otherwise defaults to 4.
        },
        install_if_missing=False,  # Should already be on PATH
    )
    source.check()
    source.set_streams(["products", "users", "purchases"])
    return source


@pytest.fixture(scope="function")  # Each test gets a fresh source-faker instance.
def source_faker_seed_b():
    """Fixture to return a source-faker connector instance."""
    source = ab.get_connector(
        "source-faker",
        config={
            "count": FAKER_SCALE_B,
            "seed": SEED_B,
            "parallelism": 16,  # Otherwise defaults to 4.
        },
        install_if_missing=False,  # Should already be on PATH
    )
    source.check()
    source.set_streams(["products", "users", "purchases"])
    return source


@pytest.fixture(scope="function")
def duckdb_cache() -> Generator[ab.DuckDBCache, None, None]:
    """Fixture to return a fresh cache."""
    cache: ab.DuckDBCache = ab.new_local_cache()
    yield cache
    # TODO: Delete cache DB file after test is complete.
    return


def test_faker_pks(
    source_faker_seed_a: ab.Source,
    duckdb_cache: ab.DuckDBCache,
) -> None:
    """Test that the append strategy works as expected."""

    catalog: ConfiguredAirbyteCatalog = source_faker_seed_a.configured_catalog

    assert len(catalog.streams) == 3
    assert catalog.streams[0].primary_key
    assert catalog.streams[1].primary_key
    assert catalog.streams[2].primary_key

    read_result = source_faker_seed_a.read(duckdb_cache, write_strategy="append")
    assert read_result.cache._get_primary_keys("products") == ["id"]
    assert read_result.cache._get_primary_keys("users") == ["id"]
    assert read_result.cache._get_primary_keys("purchases") == ["id"]


def test_replace_strategy(
    source_faker_seed_a: ab.Source,
    duckdb_cache: ab.DuckDBCache,
) -> None:
    """Test that the append strategy works as expected."""

    for _ in range(3):
        result = source_faker_seed_a.read(
            duckdb_cache, write_strategy="replace", force_full_refresh=True
        )
        assert len(result.cache.streams) == 3
        assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS
        assert len(list(result.cache.streams["users"])) == FAKER_SCALE_A
        assert len(list(result.cache.streams["purchases"])) == FAKER_SCALE_A


def test_append_strategy(
    source_faker_seed_a: ab.Source,
    duckdb_cache: ab.DuckDBCache,
) -> None:
    """Test that the append strategy works as expected."""

    for iteration in range(1, 4):
        result = source_faker_seed_a.read(duckdb_cache, write_strategy="append")
        assert len(result.cache.streams) == 3
        assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS * iteration
        assert len(list(result.cache.streams["users"])) == FAKER_SCALE_A * iteration
        assert len(list(result.cache.streams["purchases"])) == FAKER_SCALE_A * iteration


@pytest.mark.parametrize("strategy", ["merge", "auto"])
def test_merge_strategy(
    strategy: str,
    source_faker_seed_a: ab.Source,
    source_faker_seed_b: ab.Source,
    duckdb_cache: ab.DuckDBCache,
) -> None:
    """Test that the merge strategy works as expected.

    Since all streams have primary keys, we should expect the auto strategy to be identical to the
    merge strategy.
    """

    # First run, seed A (counts should match the scale or the product count)
    result = source_faker_seed_a.read(duckdb_cache, write_strategy=strategy)
    assert len(result.cache.streams) == 3
    assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS
    assert len(list(result.cache.streams["users"])) == FAKER_SCALE_A
    assert len(list(result.cache.streams["purchases"])) == FAKER_SCALE_A

    # Second run, also seed A (should have same exact data, no change in counts)
    result = source_faker_seed_a.read(duckdb_cache, write_strategy=strategy)
    assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS
    assert len(list(result.cache.streams["users"])) == FAKER_SCALE_A
    assert len(list(result.cache.streams["purchases"])) == FAKER_SCALE_A

    # Third run, seed B - should increase record count to the scale of B, which is greater than A.
    # TODO: See if we can reliably predict the exact number of records, since we use fixed seeds.
    result = source_faker_seed_b.read(duckdb_cache, write_strategy=strategy)
    assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS
    assert len(list(result.cache.streams["users"])) == FAKER_SCALE_B
    assert len(list(result.cache.streams["purchases"])) == FAKER_SCALE_B

    # Third run, seed A again - count should stay at scale B, since A is smaller.
    # TODO: See if we can reliably predict the exact number of records, since we use fixed seeds.
    result = source_faker_seed_a.read(duckdb_cache, write_strategy=strategy)
    assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS
    assert len(list(result.cache.streams["users"])) == FAKER_SCALE_B
    assert len(list(result.cache.streams["purchases"])) == FAKER_SCALE_B
