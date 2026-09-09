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
