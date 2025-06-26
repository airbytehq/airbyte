# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Run acceptance tests in PyTest.

These tests leverage the same `acceptance-test-config.yml` configuration files as the
acceptance tests in CAT, but they run in PyTest instead of CAT. This allows us to run
the acceptance tests in the same local environment as we are developing in, speeding
up iteration cycles.
"""

from __future__ import annotations

import tempfile
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import orjson
import pytest
import yaml
from pydantic import BaseModel
from source_s3.v4.source import SourceS3

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
    Type,
)
from airbyte_cdk.test import entrypoint_wrapper


if TYPE_CHECKING:
    from airbyte_cdk import Source


ACCEPTANCE_TEST_CONFIG_PATH = Path("acceptance-test-config.yml")


class AcceptanceTestInstance(BaseModel):
    """Acceptance test instance, as a Pydantic model.

    This class represents an acceptance test instance, which is a single test case
    that can be run against a connector. It is used to deserialize and validate the
    acceptance test configuration file.
    """

    class AcceptanceTestExpectRecords(BaseModel):
        path: Path
        exact_order: bool = False

    class AcceptanceTestFileTypes(BaseModel):
        skip_test: bool
        bypass_reason: str

    config_path: Path
    configured_catalog_path: Path | None = None
    timeout_seconds: int | None = None
    expect_records: AcceptanceTestExpectRecords | None = None
    file_types: AcceptanceTestFileTypes | None = None
    status: Literal["succeed", "failed"] | None = None

    @property
    def expect_exception(self) -> bool:
        return self.status and self.status == "failed"

    @property
    def instance_name(self) -> str:
        return self.config_path.stem


def get_acceptance_tests(category: str) -> list[AcceptanceTestInstance]:
    all_tests_config = yaml.safe_load(ACCEPTANCE_TEST_CONFIG_PATH.read_text())
    return [
        AcceptanceTestInstance.model_validate(test)
        for test in all_tests_config["acceptance_tests"][category]["tests"]
        if "iam_role" not in test["config_path"]
    ]


# TODO: Convert to a CDK class for better reuse and portability.
# class TestSourceAcceptanceTestSuiteBase:
#     """Test suite for acceptance tests."""

SOURCE_CLASS: type[Source] = SourceS3


def run_test_job(
    verb: Literal["read", "check", "discover"],
    test_instance: AcceptanceTestInstance,
    catalog: dict | None = None,
) -> entrypoint_wrapper.EntrypointOutput:
    """Run a test job from provided CLI args and return the result."""
    args = [verb]
    if test_instance.config_path:
        args += ["--config", str(test_instance.config_path)]

    catalog_path: Path | None = None
    if verb not in ["discover", "check"]:
        if catalog:
            # Write the catalog to a temp json file and pass the path to the file as an argument.
            catalog_path = Path(tempfile.gettempdir()) / "airbyte-test" / f"temp_catalog_{uuid.uuid4().hex}.json"
            catalog_path.parent.mkdir(parents=True, exist_ok=True)
            catalog_path.write_text(orjson.dumps(catalog).decode())
        elif test_instance.configured_catalog_path:
            catalog_path = Path(test_instance.configured_catalog_path)

        if catalog_path:
            args += ["--catalog", str(catalog_path)]

    # This is a bit of a hack because the source needs the catalog early.
    # Because it *also* can fail, we have ot redundantly wrap it in a try/except block.
    try:
        source: Source = SOURCE_CLASS.create(
            configured_catalog_path=catalog_path,
        )
    except Exception as ex:
        if not test_instance.expect_exception:
            raise

        return entrypoint_wrapper.EntrypointOutput(
            messages=[],
            uncaught_exception=ex,
        )

    result: entrypoint_wrapper.EntrypointOutput = entrypoint_wrapper._run_command(  # noqa: SLF001  # Non-public API
        source=source,
        args=args,
        expecting_exception=test_instance.expect_exception,
    )
    if result.errors and not test_instance.expect_exception:
        raise AssertionError(
            "\n\n".join(
                [str(err.trace.error).replace("\\n", "\n") for err in result.errors],
            )
        )

    if test_instance.expect_exception and not result.errors:
        raise AssertionError("Expected exception but got none.")  # noqa: TRY003

    return result


@pytest.mark.parametrize(
    "instance",
    get_acceptance_tests("full_refresh"),
    ids=lambda instance: instance.instance_name,
)
def test_full_refresh(instance: AcceptanceTestInstance) -> None:
    """Run acceptance tests."""
    result = run_test_job(
        "read",
        test_instance=instance,
    )
    if not result.records:
        raise AssertionError("Expected records but got none.")  # noqa: TRY003


@pytest.mark.parametrize(
    "instance",
    get_acceptance_tests("basic_read"),
    ids=lambda instance: instance.instance_name,
)
def test_basic_read(instance: AcceptanceTestInstance) -> None:
    """Run acceptance tests."""
    discover_result = run_test_job(
        "discover",
        test_instance=instance,
    )
    assert discover_result.catalog, "Expected a non-empty catalog."
    configured_catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=stream,
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append_dedup,
            )
            for stream in discover_result.catalog.catalog.streams
        ]
    )
    result = run_test_job(
        "read",
        test_instance=instance,
        catalog=configured_catalog,
    )

    if not result.records:
        raise AssertionError("Expected records but got none.")  # noqa: TRY003


@pytest.mark.parametrize(
    "instance",
    get_acceptance_tests("basic_read"),
    ids=lambda instance: instance.instance_name,
)
def test_fail_with_bad_catalog(instance: AcceptanceTestInstance) -> None:
    """Test that a bad catalog fails."""
    invalid_configured_catalog = ConfiguredAirbyteCatalog(
        streams=[
            # Create ConfiguredAirbyteStream which is deliberately invalid
            # with regard to the Airbyte Protocol.
            # This should cause the connector to fail.
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="__AIRBYTE__stream_that_does_not_exist",
                    json_schema={"type": "object", "properties": {"f1": {"type": "string"}}},
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode="INVALID",
                destination_sync_mode="INVALID",
            )
        ]
    )
    # Set expected status to "failed" to ensure the test fails if the connector.
    instance.status = "failed"
    result = run_test_job(
        "read",
        test_instance=instance,
        catalog=asdict(invalid_configured_catalog),
    )
    assert result.errors, "Expected errors but got none."
    assert result.trace_messages, "Expected trace messages but got none."


@pytest.mark.parametrize(
    "instance",
    get_acceptance_tests("connection"),
    ids=lambda instance: instance.instance_name,
)
def test_check(instance: AcceptanceTestInstance) -> None:
    """Run acceptance tests."""
    result: entrypoint_wrapper.EntrypointOutput = run_test_job(
        "check",
        test_instance=instance,
    )
    conn_status_messages: list[AirbyteMessage] = [msg for msg in result._messages if msg.type == Type.CONNECTION_STATUS]  # noqa: SLF001  # Non-public API
    assert len(conn_status_messages) == 1, "Expected exactly one CONNECTION_STATUS message. Got: \n" + "\n".join(result._messages)


@pytest.mark.parametrize(
    "instance",
    get_acceptance_tests("full_refresh"),
    ids=lambda instance: instance.instance_name,
)
def test_discover(instance: AcceptanceTestInstance) -> None:
    """Run acceptance tests."""
    run_test_job(
        "check",
        test_instance=instance,
    )
