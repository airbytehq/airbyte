"""Run a subset of acceptance tests in PyTest.

This test file provides a means to easily step through a subset of acceptance tests, debugging
and verifying the behavior of the source-s3 connector. The tests are redundant with CAT, but
are much faster to run and easier to debug.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import BaseModel
from source_s3.run import get_source

from airbyte_cdk import AirbyteEntrypoint, AirbyteMessage, AirbyteTracedException, Type, launch


class AcceptanceTestExpectRecords(BaseModel):
    path: str
    exact_order: bool = False


class AcceptanceTestFileTypes(BaseModel):
    skip_test: bool
    bypass_reason: str


class AcceptanceTestInstance(BaseModel):
    config_path: str
    timeout_seconds: int
    expect_records: AcceptanceTestExpectRecords | None = None
    file_types: AcceptanceTestFileTypes | None = None


class AcceptanceTestFullRefreshInstance(AcceptanceTestInstance):
    config_path: str
    timeout_seconds: int
    expect_records: AcceptanceTestExpectRecords | None = None
    file_types: AcceptanceTestFileTypes | None = None
    configured_catalog_path: str


def get_tests(category: str) -> list[AcceptanceTestInstance]:
    all_tests_config = yaml.safe_load(Path("acceptance-test-config.yml").read_text())
    if category == "basic_read" and category in all_tests_config["acceptance_tests"]:
        return [AcceptanceTestInstance.model_validate(test) for test in all_tests_config["acceptance_tests"][category]["tests"]]

    if category == "full_refresh" and category in all_tests_config["acceptance_tests"]:
        return [
            AcceptanceTestFullRefreshInstance.model_validate(
                test,
            )
            for test in all_tests_config["acceptance_tests"][category]["tests"]
        ]

    return []


@pytest.mark.parametrize("instance", get_tests("full_refresh"), ids=lambda instance: instance.config_path.split("/")[-1])
def test_full_refresh(instance: AcceptanceTestFullRefreshInstance) -> None:
    """Run acceptance tests."""
    args = [
        "read",
        "--config",
        instance.config_path,
        "--catalog",
        instance.configured_catalog_path,
    ]
    source = get_source(args=args)
    assert source
    launch(source, args=args)


def test_invalid_config(capsys: pytest.CaptureFixture[str]) -> None:
    """Ensure that the invalid config is properly reported."""

    args = [
        "check",
        "--config",
        "integration_tests/invalid_config.json",
    ]
    source = get_source(args=args)
    assert source
    try:
        launch(source, args=args)
    except AirbyteTracedException as ex:
        captured = capsys.readouterr()
        if "ConfigError" not in captured.err:
            raise AssertionError(  # noqa: TRY003
                "The `CHECK` exception was raised but not printed.",
            ) from ex

        raise AssertionError(  # noqa: TRY003
            "Expected the exception printed, not raised.",
        ) from ex
    except Exception as ex:
        captured = capsys.readouterr()
        assert "ConfigError" not in captured.err, "The `CHECK` exception was not printed."

        raise AssertionError(  # noqa: TRY003
            "Unexpected exception raised during `CHECK`.",
        ) from ex

    else:
        # No exception was raised.
        captured = capsys.readouterr()
        assert "expected_output" in captured.out, "The `CHECK` exception was not printed."
