# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Mapping

import pytest

from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit

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


def test_migrated_config_passes_the_new_spec(tmp_path):
    """The `minimum: 2` bump is only safe because spec validation runs after the migration."""
    config = {**BASE_CONFIG, "num_workers": 1}
    source = get_source(config=dict(config))

    check_config_against_spec_or_exit(source.configure(config=dict(config), temp_dir=str(tmp_path)), source.spec(None))


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

    The migration alone is not enough on the first sync after an upgrade: the CDK (7.23.8 and later) builds the
    ConcurrencyLevel from the pre-migration config, so a stored `1` would still run one worker for
    exactly the sync that needs two. Reaching into the thread pool is the only way to observe the
    effective value.
    """
    config = dict(BASE_CONFIG)
    if stored_num_workers is not None:
        config["num_workers"] = stored_num_workers

    source = get_source(config=config)

    assert source._concurrent_source._threadpool._threadpool._max_workers == expected_threads


@pytest.mark.parametrize("stored_page_size", [100, "100"], ids=["int", "numeric-string"])
def test_page_size_old_default_is_migrated_to_1000(stored_page_size, tmp_path):
    """The setup form saved the old spec default of 100, so most configs carry a 100 nobody chose."""
    migrated = _configure({**BASE_CONFIG, "page_size": stored_page_size}, tmp_path)

    assert migrated["page_size"] == 1000
    assert isinstance(migrated["page_size"], int)


@pytest.mark.parametrize("page_size", [1, 50, 99, 101, 500, 1000])
def test_page_size_other_than_old_default_is_left_alone(page_size, tmp_path):
    """Any value other than the old default was set on purpose, typically lowered after timeouts."""
    migrated = _configure({**BASE_CONFIG, "page_size": page_size}, tmp_path)

    assert migrated["page_size"] == page_size


def test_unset_page_size_is_not_added(tmp_path):
    """Configs without the field fall back to the manifest default of 1000, so the migration must not materialize it."""
    migrated = _configure(BASE_CONFIG, tmp_path)

    assert "page_size" not in migrated


def test_page_size_migration_is_idempotent(tmp_path):
    once = _configure({**BASE_CONFIG, "page_size": 100}, tmp_path)
    twice = _configure(once, tmp_path)

    assert twice == once


def test_page_size_migration_is_persisted(tmp_path, capsys):
    """`page_size` is a top-level field, so the migrated config differs from the input and is emitted as a
    CONNECTOR_CONFIG control message for the platform to save. A nested field would not be, because the CDK
    only takes a shallow copy of the config before migrating it."""
    get_source(config={**BASE_CONFIG, "page_size": 100})

    control_messages = [json.loads(line) for line in capsys.readouterr().out.splitlines() if '"CONNECTOR_CONFIG"' in line]
    assert [message["control"]["connectorConfig"]["config"]["page_size"] for message in control_messages] == [1000]


def test_page_size_unchanged_config_is_not_emitted(capsys):
    get_source(config={**BASE_CONFIG, "page_size": 50})

    assert '"CONNECTOR_CONFIG"' not in capsys.readouterr().out


def test_spec_page_size_defaults_to_1000():
    page_size = get_source(config=dict(BASE_CONFIG)).spec(None).connectionSpecification["properties"]["page_size"]

    assert (page_size["default"], page_size["minimum"], page_size["maximum"]) == (1000, 1, 1000)
