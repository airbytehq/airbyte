# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping

import pytest

from .conftest import get_source


BASE_CONFIG: Mapping[str, Any] = {
    "subdomain": "sandbox",
    "credentials": {"credentials": "api_token", "email": "integration-test@airbyte.io", "api_token": "token"},
}


def _configure(config: Mapping[str, Any], tmp_path) -> Mapping[str, Any]:
    source = get_source(config=dict(config))
    return source.configure(config=dict(config), temp_dir=str(tmp_path))


def test_num_workers_one_is_migrated_to_two(tmp_path):
    """A single worker serializes every stream behind the `tickets` walk, so it is raised to the new minimum."""
    migrated = _configure({**BASE_CONFIG, "num_workers": 1}, tmp_path)

    assert migrated["num_workers"] == 2
    assert isinstance(migrated["num_workers"], int)


@pytest.mark.parametrize("num_workers", [2, 4, 10, 40])
def test_num_workers_at_or_above_minimum_is_left_alone(num_workers, tmp_path):
    migrated = _configure({**BASE_CONFIG, "num_workers": num_workers}, tmp_path)

    assert migrated["num_workers"] == num_workers


def test_unset_num_workers_is_not_added(tmp_path):
    """Configs without the field keep falling back to the manifest default, so the migration must not materialize it."""
    migrated = _configure(BASE_CONFIG, tmp_path)

    assert "num_workers" not in migrated


def test_spec_declares_two_as_the_minimum():
    spec = get_source(config=dict(BASE_CONFIG)).spec(None)

    assert spec.connectionSpecification["properties"]["num_workers"]["minimum"] == 2


@pytest.mark.parametrize(
    "stored_num_workers, expected_threads",
    [(1, 2), (2, 2), (4, 4), (None, 4)],
    ids=["one-is-clamped", "two", "four", "unset-uses-manifest-default"],
)
def test_concurrency_never_drops_below_two(stored_num_workers, expected_threads):
    """`concurrency_level` clamps as well as the migration.

    The migration alone is not enough on the first sync after an upgrade: CDK 7.23.8 builds the
    ConcurrencyLevel from the pre-migration config, so a stored `1` would still run one worker for
    exactly the sync that needs two. Reaching into the thread pool is the only way to observe the
    effective value.
    """
    config = dict(BASE_CONFIG)
    if stored_num_workers is not None:
        config["num_workers"] = stored_num_workers

    source = get_source(config=config)

    assert source._concurrent_source._threadpool._threadpool._max_workers == expected_threads
