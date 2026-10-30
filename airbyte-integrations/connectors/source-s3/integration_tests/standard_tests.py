# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""FAST Airbyte Standard Tests for source-s3, run in-process by `poe test-standard-tests`.

The suite that `poe test-standard-tests` generates cannot build the source: the `source_s3` package
does not export `SourceS3` (it lives in `source_s3.v4`), its constructor also takes a stream reader
and a spec class, and it takes its stream schemas from the catalog it is built with. This suite
builds it the way `run.py` does.

The file is not named `test_*.py`, so that `poe test-integration-tests` does not collect it.
"""

import json
from pathlib import Path
from typing import Any

from source_s3.v4 import Config, Cursor, SourceS3, SourceS3StreamReader
from source_s3.v4.availability_strategy import SourceS3AvailabilityStrategy

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
    # As `SourceS3.create()` does: config and state reach the source with the command.
    stream_reader = SourceS3StreamReader()
    return SourceS3(
        stream_reader=stream_reader,
        availability_strategy=SourceS3AvailabilityStrategy(stream_reader),
        spec_class=Config,
        cursor_cls=Cursor,
        catalog=catalog,
        config=None,
        state=None,
    )


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
