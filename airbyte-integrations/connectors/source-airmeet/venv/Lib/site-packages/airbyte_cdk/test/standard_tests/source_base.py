# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Base class for source test suites."""

from dataclasses import asdict
from typing import TYPE_CHECKING

import pytest

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)
from airbyte_cdk.test.models import (
    ConnectorTestScenario,
)
from airbyte_cdk.test.standard_tests._job_runner import run_test_job
from airbyte_cdk.test.standard_tests.connector_base import (
    ConnectorTestSuiteBase,
)

if TYPE_CHECKING:
    from airbyte_cdk.test import entrypoint_wrapper


class SourceTestSuiteBase(ConnectorTestSuiteBase):
    """Base class for source test suites.

    This class provides a base set of functionality for testing source connectors, and it
    inherits all generic connector tests from the `ConnectorTestSuiteBase` class.
    """

    def test_check(
        self,
        scenario: ConnectorTestScenario,
    ) -> None:
        """Run standard `check` tests on the connector.

        Assert that the connector returns a single CONNECTION_STATUS message.
        This test is designed to validate the connector's ability to establish a connection
        and return its status with the expected message type.
        """
        result: entrypoint_wrapper.EntrypointOutput = run_test_job(
            self.create_connector(scenario),
            "check",
            test_scenario=scenario,
            connector_root=self.get_connector_root_dir(),
        )
        num_status_messages = len(result.connection_status_messages)
        assert num_status_messages == 1, (
            f"Expected exactly one CONNECTION_STATUS message. Got {num_status_messages}: \n"
            + "\n".join([str(m) for m in result.get_message_iterator()])
        )

    def test_discover(
        self,
        scenario: ConnectorTestScenario,
    ) -> None:
        """Standard test for `discover`."""
        if scenario.expected_outcome.expect_exception():
            # If the scenario expects an exception, we can't ensure it specifically would fail
            # in discover, because some discover implementations do not need to make a connection.
            # We skip this test in that case.
            pytest.skip("Skipping discover test for scenario that expects an exception.")
            return

        run_test_job(
            self.create_connector(scenario),
            "discover",
            connector_root=self.get_connector_root_dir(),
            test_scenario=scenario,
        )

    def test_spec(self) -> None:
        """Standard test for `spec`.

        This test does not require a `scenario` input, since `spec`
        does not require any inputs.

        We assume `spec` should always succeed and it should always generate
        a valid `SPEC` message.

        Note: the parsing of messages by type also implicitly validates that
        the generated `SPEC` message is valid JSON.
        """
        result = run_test_job(
            verb="spec",
            test_scenario=None,
            connector=self.create_connector(scenario=None),
            connector_root=self.get_connector_root_dir(),
        )
        # If an error occurs, it will be raised above.

        assert len(result.spec_messages) == 1, (
            "Expected exactly 1 spec message but got {len(result.spec_messages)}",
            result.errors,
        )

    def test_basic_read(
        self,
        scenario: ConnectorTestScenario,
    ) -> None:
        """Run standard `read` test on the connector.

        This test is designed to validate the connector's ability to read data
        from the source and return records. It first runs a `discover` job to
        obtain the catalog of streams, and then it runs a `read` job to fetch
        records from those streams.
        """
        discover_result = run_test_job(
            self.create_connector(scenario),
            "discover",
            connector_root=self.get_connector_root_dir(),
            test_scenario=scenario.without_expected_outcome(),
        )
        if scenario.expected_outcome.expect_exception() and discover_result.errors:
            # Failed as expected; we're done.
            return
        streams = discover_result.catalog.catalog.streams  # type: ignore [reportOptionalMemberAccess, union-attr]

        if scenario.empty_streams:
            # Filter out streams marked as empty in the scenario.
            empty_stream_names = [stream.name for stream in scenario.empty_streams]
            streams = [s for s in streams if s.name not in empty_stream_names]

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

        if scenario.expected_outcome.expect_success() and not result.records:
            raise AssertionError("Expected records but got none.")

    def test_fail_read_with_bad_catalog(
        self,
        scenario: ConnectorTestScenario,
    ) -> None:
        """Standard test for `read` when passed a bad catalog file."""
        invalid_configured_catalog = ConfiguredAirbyteCatalog(
            streams=[
                # Create ConfiguredAirbyteStream which is deliberately invalid
                # with regard to the Airbyte Protocol.
                # This should cause the connector to fail.
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(
                        name="__AIRBYTE__stream_that_does_not_exist",
                        json_schema={
                            "type": "object",
                            "properties": {"f1": {"type": "string"}},
                        },
                        supported_sync_modes=[SyncMode.full_refresh],
                    ),
                    sync_mode="INVALID",  # type: ignore [reportArgumentType]
                    destination_sync_mode="INVALID",  # type: ignore [reportArgumentType]
                ),
            ],
        )
        result: entrypoint_wrapper.EntrypointOutput = run_test_job(
            self.create_connector(scenario),
            "read",
            connector_root=self.get_connector_root_dir(),
            test_scenario=scenario.with_expecting_failure(),  # Expect failure due to bad catalog
            catalog=asdict(invalid_configured_catalog),
        )
        assert result.errors, "Expected errors but got none."
        assert result.trace_messages, "Expected trace messages but got none."
