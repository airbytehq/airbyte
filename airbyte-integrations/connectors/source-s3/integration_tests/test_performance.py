"""Run performance tests in PyTest."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import BaseModel
from source_s3 import SourceS3

from airbyte_cdk import launch


class AcceptanceTestExpectRecords(BaseModel):
    path: str
    exact_order: bool = False


class AcceptanceTestFileTypes(BaseModel):
    skip_test: bool
    bypass_reason: str


class AcceptanceTestInstance(BaseModel):
    config_path: str
    timeout_seconds: int | None = None
    expect_records: AcceptanceTestExpectRecords | None = None
    file_types: AcceptanceTestFileTypes | None = None


class AcceptanceTestFullRefreshInstance(AcceptanceTestInstance):
    config_path: str
    configured_catalog_path: str
    timeout_seconds: int = None
    expect_records: AcceptanceTestExpectRecords | None = None
    file_types: AcceptanceTestFileTypes | None = None


class AcceptanceTestPerformanceInstance(AcceptanceTestInstance):
    config_path: str
    configured_catalog_path: str


def get_tests(category: str) -> list[AcceptanceTestInstance]:
    all_tests_config = yaml.safe_load(Path("performance-test-config.yml").read_text())
    tests: list[AcceptanceTestInstance] = []
    if category == "basic_read" and category in all_tests_config["performance_tests"]:
        tests += [AcceptanceTestInstance.model_validate(test) for test in all_tests_config["performance_tests"][category]["tests"]]

    if category == "full_refresh" and category in all_tests_config["performance_tests"]:
        tests += [
            AcceptanceTestFullRefreshInstance.model_validate(
                test,
            )
            for test in all_tests_config["performance_tests"][category]["tests"]
        ]

    if category == "performance" and category in all_tests_config["performance_tests"]:
        tests += [AcceptanceTestPerformanceInstance.model_validate(test) for test in all_tests_config["performance_tests"][category]["tests"]]

    return [
        test for test in tests
        # if "iam_role" not in test.config_path
    ]


@pytest.mark.parametrize("instance", get_tests("full_refresh"), ids=lambda instance: instance.config_path.split("/")[-1])
def test_performance(instance: AcceptanceTestFullRefreshInstance) -> None:
    """Run performance tests."""
    args = [
        "read",
        "--config",
        instance.config_path,
        "--catalog",
        instance.configured_catalog_path,
    ]
    source = SourceS3.launch(args=args)
    assert source
    launch(source, args=args)
