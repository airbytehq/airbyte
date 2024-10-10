# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum

import pytest
from google.cloud import storage

AIRBYTE_COMMANDS = ["spec", "check", "discover", "read"]


def get_option_or_fail(config: pytest.Config, option: str) -> str:
    if option_value := config.getoption(option):
        return option_value
    pytest.fail(f"Missing required option: {option}")


def pytest_addoption(parser) -> None:
    parser.addoption(
        "--package-name",
        help="The connector package name on which the tests will run: e.g. airbyte-source-faker",
    )
    parser.addoption(
        "--control-version",
        help="The control version used for regression testing.",
    )
    parser.addoption(
        "--target-version",
        help="The target version used for regression and validation testing. Defaults to dev.",
    )


@dataclass
class BundledArtifact:
    package_name: str
    package_version: str
    airbyte_command: str
    data: dict
    session_id: int

    @classmethod
    def from_blob(cls, blob):
        blob_name_parts = blob.name.split("/")
        return BundledArtifact(
            package_name=blob_name_parts[0],
            package_version=blob_name_parts[1],
            airbyte_command=blob_name_parts[2],
            session_id=blob_name_parts[-1].split("_")[0],
            data=json.loads(blob.download_as_string()),
        )

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]
        try:
            return super().__getattr__(item)
        except AttributeError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")


def get_artifacts_for_version(artifacts_bucket_name, package_name, package_version):

    client = storage.Client(project="ab-connector-integration-test")

    # Get the bucket
    bucket = client.bucket(artifacts_bucket_name)

    artifacts = []
    for airbyte_command in AIRBYTE_COMMANDS:
        for blob in bucket.list_blobs(prefix=f"{package_name}/{package_version}/{airbyte_command}"):
            artifacts.append(BundledArtifact.from_blob(blob))
    if not artifacts:
        pytest.fail(f"Could not find bundled artifacts for {package_name} on version {package_version}")
    return artifacts


@pytest.fixture(scope="session")
def artifacts_bucket_name():
    return "poc-connector-canary-testing"


@pytest.fixture(scope="session")
def package_name(pytestconfig):
    return get_option_or_fail(pytestconfig, "--package-name")


@pytest.fixture(scope="session")
def control_version(pytestconfig):
    return get_option_or_fail(pytestconfig, "--control-version")


@pytest.fixture(scope="session")
def target_version(pytestconfig):
    return get_option_or_fail(pytestconfig, "--target-version")


@pytest.fixture(scope="session")
def control_artifacts(package_name, control_version, artifacts_bucket_name):
    return get_artifacts_for_version(artifacts_bucket_name, package_name, control_version)


@pytest.fixture(scope="session")
def target_artifacts(package_name, target_version, artifacts_bucket_name):
    return get_artifacts_for_version(artifacts_bucket_name, package_name, target_version)


@pytest.fixture(scope="session")
def control_and_target_artifacts_per_sessions(control_artifacts, target_artifacts):
    control_sessions = {a.session_id: a for a in control_artifacts}
    target_sessions = {a.session_id: a for a in target_artifacts}
    control_and_target_artifacts_per_sessions = []

    for session_id, control_session_artifacts in control_sessions.items():
        if session_id in target_sessions:
            control_and_target_artifacts_per_sessions.append((control_session_artifacts, target_sessions[session_id]))
    return control_and_target_artifacts_per_sessions
