"""Integration tests which leverage the source-faker connector to test the framework end-to-end.

Since source-faker is included in dev dependencies, we can assume `source-faker` is installed
and available on PATH for the poetry-managed venv.
"""
from __future__ import annotations
from collections.abc import Generator

import pytest

import airbyte_lib as ab
from airbyte_cdk.models import ConfiguredAirbyteCatalog

DEFAULT_FAKER_SCALE = 1_000  # Number of records in each of the 'users' and 'purchases' streams.
NUM_PRODUCTS = 100            # This is always the same count, regardless of faker scale.
SEED_A = 1234
SEED_B = 5678


@pytest.fixture(scope="function")  # Each test gets a fresh source-faker instance.
def source_faker_seed_a():
    """Fixture to return a source-faker connector instance."""
    source = ab.get_connector(
        "source-faker",
        config={
            "count": DEFAULT_FAKER_SCALE,
            "seed": SEED_A,
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
            "count": DEFAULT_FAKER_SCALE,
            "seed": SEED_B,
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

    read_result = source_faker_seed_a.read(duckdb_cache, strategy="append")
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
            duckdb_cache, strategy="replace", force_full_refresh=True
        )
        assert len(result.cache.streams) == 3
        assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS
        assert len(list(result.cache.streams["users"])) == DEFAULT_FAKER_SCALE
        assert len(list(result.cache.streams["purchases"])) == DEFAULT_FAKER_SCALE


def test_append_strategy(
    source_faker_seed_a: ab.Source,
    duckdb_cache: ab.DuckDBCache,
) -> None:
    """Test that the append strategy works as expected."""

    for iteration in range(1, 4):
        result = source_faker_seed_a.read(duckdb_cache, strategy="append")
        assert len(result.cache.streams) == 3
        assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS * iteration
        assert len(list(result.cache.streams["users"])) == DEFAULT_FAKER_SCALE * iteration
        assert len(list(result.cache.streams["purchases"])) == DEFAULT_FAKER_SCALE * iteration


def test_merge_strategy(
    source_faker_seed_a: ab.Source,
    source_faker_seed_b: ab.Source,
    duckdb_cache: ab.DuckDBCache,
) -> None:
    """Test that the merge strategy works as expected."""

    # First run, seed A (counts should match the scale or the product count)
    result = source_faker_seed_a.read(duckdb_cache, strategy="merge")
    assert len(result.cache.streams) == 2
    # assert len(result.cache.streams["products"]) == NUM_PRODUCTS
    assert len(list(result.cache.streams["users"])) == DEFAULT_FAKER_SCALE
    assert len(list(result.cache.streams["purchases"])) == DEFAULT_FAKER_SCALE

    # Second run, also seed A (should have same exact data, no change in counts)
    result = source_faker_seed_a.read(duckdb_cache, strategy="merge")
    # assert len(result.cache.streams["products"]) == NUM_PRODUCTS
    assert len(list(result.cache.streams["users"])) == DEFAULT_FAKER_SCALE
    assert len(list(result.cache.streams["purchases"])) == DEFAULT_FAKER_SCALE

    # Third run, seed B (should increase record count, but not double)
    # TODO: See if we can reliably predict the exact number of records, since we use fixed seeds.
    result = source_faker_seed_b.read(duckdb_cache, strategy="merge")
    # assert NUM_PRODUCTS < len(result.cache.streams["products"]) > NUM_PRODUCTS * 2
    assert DEFAULT_FAKER_SCALE < len(list(result.cache.streams["users"])) < DEFAULT_FAKER_SCALE * 2
    assert DEFAULT_FAKER_SCALE < len(list(result.cache.streams["purchases"])) < DEFAULT_FAKER_SCALE * 2

    users_count, purchases_count, products_count = (
        len(list(result.cache.streams["users"])),
        len(list(result.cache.streams["purchases"])),
        len(list(result.cache.streams["products"])),
    )

    # Fourth run, also seed B (record count should not increase from last run)
    result = source_faker_seed_b.read(duckdb_cache, strategy="merge")
    assert len(result.cache.streams) == 3
    assert len(list(result.cache.streams["products"])) == products_count
    assert len(list(result.cache.streams["users"])) == users_count
    assert len(list(result.cache.streams["purchases"])) == products_count


def test_auto_strategy(
    source_faker_seed_a: ab.Source,
    source_faker_seed_b: ab.Source,
    duckdb_cache: ab.DuckDBCache,
) -> None:
    """Test that the auto strategy works as expected.

    Auto strategy should use the logic:
    - If there's a primary key, use merge.
    - Else, if there's an incremental key, use append.
    - Else, use full replace (table swap).

    Since source-faker has primary keys, we should always expect merge behavior.
    """

    # First run, seed A (counts should match the scale or the product count)
    result = source_faker_seed_a.read(duckdb_cache, strategy="auto")
    assert len(result.cache.streams) == 3
    assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS
    assert len(list(result.cache.streams["users"])) == DEFAULT_FAKER_SCALE
    assert len(list(result.cache.streams["purchases"])) == DEFAULT_FAKER_SCALE

    # Second run, also seed A (should have same exact data, no change in counts)
    result = source_faker_seed_a.read(duckdb_cache, strategy="auto")
    assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS
    assert len(list(result.cache.streams["users"])) == DEFAULT_FAKER_SCALE
    assert len(list(result.cache.streams["purchases"])) == DEFAULT_FAKER_SCALE

    # Third run, seed B (should increase record count, but not double)
    # TODO: See if we can reliably predict the exact number of records, since we use fixed seeds.
    result = source_faker_seed_b.read(duckdb_cache, strategy="auto")
    assert len(list(result.cache.streams["products"])) == NUM_PRODUCTS
    assert DEFAULT_FAKER_SCALE < len(list(result.cache.streams["users"])) < DEFAULT_FAKER_SCALE * 2
    assert DEFAULT_FAKER_SCALE < len(list(result.cache.streams["purchases"])) < DEFAULT_FAKER_SCALE * 2

    users_count, purchases_count = (
        len(list(result.cache.streams["users"])),
        len(list(result.cache.streams["purchases"])),
    )

    # Fourth run, also seed B (record count should not increase from last run)
    result = source_faker_seed_b.read(duckdb_cache, strategy="auto")
    assert len(list(result.cache.streams["users"])) == users_count
    assert len(list(result.cache.streams["purchases"])) == purchases_count
