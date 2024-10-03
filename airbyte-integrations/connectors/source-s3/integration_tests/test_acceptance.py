"""Run acceptance tests in PyTest.

These tests leverage the same `acceptance-test-config.yml` configuration files as the
acceptance tests in CAT, but they run in PyTest instead of CAT. This allows us to run
the acceptance tests in the same local environment as we are developing in, speeding
up iteration cycles.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import yaml
from pydantic import BaseModel
from source_s3.run import get_source

from airbyte_cdk.test import entrypoint_wrapper


if TYPE_CHECKING:
    from airbyte_cdk import Source


class AcceptanceTestInstance(BaseModel):
    """Acceptance test instance.

    This class represents an acceptance test instance, which is a single test case
    that can be run against a connector. It is used to validate the acceptance test
    configuration file.
    """

    class AcceptanceTestExpectRecords(BaseModel):
        path: str
        exact_order: bool = False

    class AcceptanceTestFileTypes(BaseModel):
        skip_test: bool
        bypass_reason: str

    config_path: str
    configured_catalog_path: str | None = None
    timeout_seconds: int | None = None
    expect_records: AcceptanceTestExpectRecords | None = None
    file_types: AcceptanceTestFileTypes | None = None


def _get_acceptance_tests(category: str) -> list[AcceptanceTestInstance]:
    all_tests_config = yaml.safe_load(Path("acceptance-test-config.yml").read_text())
    tests: list[AcceptanceTestInstance] = []
    if category == "basic_read" and category in all_tests_config["acceptance_tests"]:
        tests += [AcceptanceTestInstance.model_validate(test) for test in all_tests_config["acceptance_tests"][category]["tests"]]

    if category == "full_refresh" and category in all_tests_config["acceptance_tests"]:
        tests += [
            AcceptanceTestInstance.model_validate(
                test,
            )
            for test in all_tests_config["acceptance_tests"][category]["tests"]
        ]

    if category == "performance" and category in all_tests_config["acceptance_tests"]:
        tests += [AcceptanceTestInstance.model_validate(test) for test in all_tests_config["acceptance_tests"][category]["tests"]]

    return [  # noqa: C416  # Ignore list comprehension suggestion
        test
        for test in tests
        # if "iam_role" not in test.config_path
    ]


def _run_test_job(
    args: list[str],
    *,
    expecting_exception: bool,
) -> None:
    source: Source | None = get_source(args=args)
    assert source

    result: entrypoint_wrapper.EntrypointOutput = entrypoint_wrapper._run_command(  # noqa: SLF001  # Non-public API
        source=source,
        args=args,
        expecting_exception=expecting_exception,
    )
    if result.errors:
        raise AssertionError(
            "\n\n".join(
                [str(err.trace.error).replace("\\n", "\n") for err in result.errors],
            )
        )


@pytest.mark.parametrize(
    "instance",
    _get_acceptance_tests("full_refresh"),
    ids=lambda instance: instance.config_path.split("/")[-1],
)
def test_full_refresh(instance: AcceptanceTestInstance) -> None:
    """Run acceptance tests."""
    _run_test_job(
        args=[
            "read",
            "--config",
            instance.config_path,
            "--catalog",
            instance.configured_catalog_path,
        ],
        expecting_exception=False,
    )


@pytest.mark.parametrize(
    "instance",
    _get_acceptance_tests("full_refresh"),
    ids=lambda instance: instance.config_path.split("/")[-1],
)
def test_check(instance: AcceptanceTestInstance) -> None:
    """Run acceptance tests."""
    _run_test_job(
        args=[
            "check",
            "--config",
            instance.config_path,
        ],
        expecting_exception=False,
    )


@pytest.mark.parametrize(
    "instance",
    _get_acceptance_tests("full_refresh"),
    ids=lambda instance: instance.config_path.split("/")[-1],
)
def test_discover(instance: AcceptanceTestInstance) -> None:
    """Run acceptance tests."""
    _run_test_job(
        args=[
            "discover",
            "--config",
            instance.config_path,
        ],
        expecting_exception=False,
    )
