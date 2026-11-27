# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""FAST Airbyte Standard Tests for source-posthog, run in-process by `poe test-standard-tests`.

The suite that `poe test-standard-tests` generates cannot build the source: its constructor requires
`catalog`, `config` and `state`. This suite builds it the way `run.py` does.

The file is not named `test_*.py`, so that `poe test-integration-tests` does not collect it.
"""

import json
from pathlib import Path
from typing import Any

from source_posthog import SourcePosthog

from airbyte_cdk.test.standard_tests import SourceTestSuiteBase


pytest_plugins = ["airbyte_cdk.test.standard_tests.pytest_hooks"]

CONNECTOR_ROOT = Path(__file__).resolve().parent.parent


def _scenario_config(scenario: Any) -> Any:
    """Return the scenario's config as `run.py` reads it from `--config`, or None without one."""
    if scenario is None:
        return None
    if scenario.config_dict is not None:
        return scenario.config_dict
    if scenario.config_path is None:
        return None
    config_path = Path(scenario.config_path)
    if not config_path.is_absolute():
        config_path = CONNECTOR_ROOT / config_path
    # A missing config file (no secrets) is reported by the test that runs the command.
    return json.loads(config_path.read_text()) if config_path.exists() else None


def _build_source(catalog: Any, config: Any, state: Any) -> Any:
    """Build the source as `run.py` does for a command with these arguments."""
    return SourcePosthog(catalog=catalog, config=config, state=state)


class TestAirbyteStandardTests(SourceTestSuiteBase):
    """The FAST Airbyte Standard Tests, with the source built as `run.py` builds it."""

    @classmethod
    def create_connector(cls, scenario: Any) -> Any:
        source = _build_source(catalog=None, config=_scenario_config(scenario), state=None)

        def read(logger: Any, config: Any, catalog: Any, state: Any = None) -> Any:
            # `run.py` builds the source with the catalog and state of the `read` command, and the
            # suite builds this one before it knows them, so read with a source built like `run.py`.
            return _build_source(catalog=catalog, config=config, state=state).read(logger, config, catalog, state)

        source.read = read
        return source
