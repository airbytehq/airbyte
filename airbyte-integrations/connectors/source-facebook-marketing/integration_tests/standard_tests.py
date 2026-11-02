# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""FAST Airbyte Standard Tests for source-facebook-marketing, run in-process by `poe test-standard-tests`.

With the airbyte-cdk version this connector pins (before 7.36), the generated `test_basic_read` reads
every discovered stream, for every config that acceptance-test-config.yml lists (connection configs
included). For this connector that read does not fit the CI step's time budget: it was still reading after 49 minutes when it was stopped.

This suite keeps the read and bounds it:

- it reads only the configs listed under `basic_read`; the other configs still run `check` and
  `discover`;
- it reads only the streams in metadata.yaml `suggestedStreams`, minus the config's `empty_streams`;
- every stream it reads must return at least one record.

This is the only CI read of records for this connector: `airbyte-cdk image test`, as connector CI
runs it, skips its Docker read (`--read-from-streams` is off by default) until the CDK release of
airbytehq/airbyte-internal-issues#17137 turns that read on.

Remove this file when the connector pins a CDK (7.36 or later) whose `test_basic_read` runs only for
`basic_read` configs, and its basic_read entries declare a `configured_catalog_path` that bounds the
read.

The file is not named `test_*.py`, so that `poe test-integration-tests` does not collect it.
"""

from collections import Counter
from pathlib import Path

import pytest
import yaml

from airbyte_cdk.models import (
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)
from airbyte_cdk.test.models import ConnectorTestScenario
from airbyte_cdk.test.standard_tests._job_runner import run_test_job
from airbyte_cdk.test.standard_tests.util import create_connector_test_suite


pytest_plugins = ["airbyte_cdk.test.standard_tests.pytest_hooks"]

CONNECTOR_DIR = Path(__file__).resolve().parent.parent

_GeneratedSuite = create_connector_test_suite(connector_directory=CONNECTOR_DIR)


def _suggested_streams() -> set[str]:
    metadata = yaml.safe_load((CONNECTOR_DIR / "metadata.yaml").read_text())
    return set(metadata["data"]["suggestedStreams"]["streams"])


def _basic_read_config_paths() -> set[Path]:
    acceptance = yaml.safe_load((CONNECTOR_DIR / "acceptance-test-config.yml").read_text())
    return {Path(test["config_path"]) for test in acceptance["acceptance_tests"]["basic_read"]["tests"]}


class TestAirbyteStandardTests(_GeneratedSuite):  # type: ignore[misc, valid-type]
    """The generated in-process suite, with `test_basic_read` bounded to the suggested streams."""

    def test_basic_read(self, scenario: ConnectorTestScenario) -> None:
        if scenario.config_path is None or Path(scenario.config_path) not in _basic_read_config_paths():
            pytest.skip(f"Config '{scenario.id}' is not listed under `basic_read`, so it is not read.")

        discover_result = run_test_job(
            self.create_connector(scenario),
            "discover",
            connector_root=self.get_connector_root_dir(),
            test_scenario=scenario.without_expected_outcome(),
        )
        if scenario.expected_outcome.expect_exception() and discover_result.errors:
            return
        empty_streams = {stream.name for stream in scenario.empty_streams or []}
        suggested = _suggested_streams()
        streams = [
            stream
            for stream in discover_result.catalog.catalog.streams  # type: ignore[union-attr]
            if stream.name in suggested and stream.name not in empty_streams
        ]
        assert streams, "None of the metadata.yaml `suggestedStreams` is discovered outside `empty_streams`."

        configured_catalog = ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    stream=stream,
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.append_dedup,
                )
                for stream in streams
            ]
        )
        result = run_test_job(
            self.create_connector(scenario),
            "read",
            test_scenario=scenario,
            connector_root=self.get_connector_root_dir(),
            catalog=configured_catalog,
        )
        if not scenario.expected_outcome.expect_success():
            return

        counts = Counter(message.record.stream for message in result.records)
        missing = sorted(stream.name for stream in streams if not counts[stream.name])
        assert not missing, (
            "Every suggested stream must return at least one record, but these returned none: "
            + ", ".join(f"'{name}'" for name in missing)
            + ". If a stream is expected to be empty for this config, list it under `empty_streams` "
            "(with a `bypass_reason`) in the config's `basic_read` entry of acceptance-test-config.yml."
        )
