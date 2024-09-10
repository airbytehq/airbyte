"""Run acceptance tests in PyTest."""

from __future__ import annotations

import contextlib
import os
from pathlib import Path

import pytest
import yaml
from pydantic import BaseModel
from source_s3.run import get_source

from airbyte_cdk import AirbyteEntrypoint, AirbyteMessage, Type, launch


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
    timeout_seconds: int
    expect_records: AcceptanceTestExpectRecords | None = None
    file_types: AcceptanceTestFileTypes | None = None
    configured_catalog_path: str


class AcceptanceTestPerformanceInstance(AcceptanceTestInstance):
    config_path: str
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

    if category == "performance" and category in all_tests_config["acceptance_tests"]:
        return [AcceptanceTestPerformanceInstance.model_validate(test) for test in all_tests_config["acceptance_tests"][category]["tests"]]

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


@pytest.mark.parametrize("instance", get_tests("performance"), ids=lambda instance: instance.config_path.split("/")[-1])
def test_performance(instance: AcceptanceTestPerformanceInstance, capsys: pytest.CaptureFixture[str]) -> None:
    """Run performance tests."""
    args = [
        "check",
        "--config",
        instance.config_path,
    ]
    source = get_source(args=args)
    launch(source, args=args)

    args = [
        "read",
        "--config",
        instance.config_path,
        "--catalog",
        instance.configured_catalog_path,
    ]

    source = get_source(args=args)
    assert source
    launch(source, args=args, out=os.devnull)
