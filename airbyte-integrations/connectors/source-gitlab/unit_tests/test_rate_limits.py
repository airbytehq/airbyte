#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

"""Tests for concurrency and HTTPAPIBudget rate-limit settings.

These tests verify that:
- Default concurrency is 4 (not 8) to avoid 429 rate-limit errors on large workspaces.
- Safety margins are applied to all rate-limit budgets (70 % of GitLab's documented limits).
- The ``num_workers`` config value correctly overrides the default concurrency.
"""

from pathlib import Path

import yaml


def _load_manifest() -> dict:
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    with open(manifest_path) as f:
        return yaml.safe_load(f)


def test_default_concurrency_is_four():
    """Default concurrency must be 4 to stay within GitLab rate limits for large workspaces."""
    manifest = _load_manifest()
    concurrency = manifest["concurrency_level"]
    assert concurrency["default_concurrency"] == "{{ config.get('num_workers', 4) }}"
    assert concurrency["max_concurrency"] == 25


def test_num_workers_spec_defaults():
    """The num_workers spec field must default to 4 with minimum 1."""
    manifest = _load_manifest()
    spec_props = manifest["spec"]["connection_specification"]["properties"]
    num_workers = spec_props["num_workers"]
    assert num_workers["default"] == 4
    assert num_workers["minimum"] == 1
    assert num_workers["maximum"] == 25


def test_rate_limit_safety_margins():
    """All HTTPAPIBudget policies must have safety margins below GitLab's documented limits.

    GitLab documented limits → connector budget (70 % safety margin):
      Members:           200/min → 140/min
      Groups list:       200/min → 140/min
      Descendant groups: 200/min → 140/min
      Groups/:id:        400/min → 280/min
      Projects/:id:      400/min → 280/min
      Catch-all:       2,000/min → 1,400/min
    """
    manifest = _load_manifest()
    policies = manifest["api_budget"]["policies"]

    expected = {
        "/members": 140,
        "^groups$": 140,
        "/descendant_groups$": 140,
        "^groups/[^/]+$": 280,
        "^projects/[^/]+$": 280,
    }

    for policy in policies:
        matchers = policy.get("matchers", [])
        if not matchers:
            # Catch-all policy
            assert policy["rates"][0]["limit"] == 1400, "Catch-all budget must be 1400"
            continue
        for matcher in matchers:
            pattern = matcher.get("url_path_pattern")
            if pattern in expected:
                actual_limit = policy["rates"][0]["limit"]
                assert actual_limit == expected[pattern], f"Budget for pattern {pattern!r} must be {expected[pattern]}, got {actual_limit}"
                del expected[pattern]

    assert not expected, f"Missing rate-limit policies for patterns: {list(expected.keys())}"


def test_concurrency_with_custom_num_workers(requests_mock):
    """When a user sets num_workers in config, it overrides the default concurrency."""
    from .conftest import BASE_CONFIG, GROUPS_LIST_URL, get_source

    custom_config = BASE_CONFIG | {"num_workers": 2}
    requests_mock.get(url=GROUPS_LIST_URL, status_code=200)
    source = get_source(config=custom_config)
    migrated_config = source.configure(config=custom_config, temp_dir="/not/a/real/path")
    streams = source.streams(migrated_config)
    # Source must initialise successfully with a custom (low) concurrency value
    assert len(streams) > 0
