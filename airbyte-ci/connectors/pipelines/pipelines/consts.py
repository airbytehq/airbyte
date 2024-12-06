#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
import platform
from enum import Enum

from dagger import Platform

PYPROJECT_TOML_FILE_PATH = "pyproject.toml"
MANIFEST_FILE_PATH = "manifest.yaml"
COMPONENTS_FILE_PATH = "components.py"
LICENSE_SHORT_FILE_PATH = "LICENSE_SHORT"
CONNECTOR_TESTING_REQUIREMENTS = [
    "pip==21.3.1",
    "mccabe==0.6.1",
    # "flake8==4.0.1",
    # "pyproject-flake8==0.0.1a2",
    "pytest==6.2.5",
    "coverage[toml]==6.3.1",
    "pytest-custom_exit_code",
]

BUILD_PLATFORMS = (Platform("linux/amd64"), Platform("linux/arm64"))

PLATFORM_MACHINE_TO_DAGGER_PLATFORM = {
    "x86_64": Platform("linux/amd64"),
    "arm64": Platform("linux/arm64"),
    "aarch64": Platform("linux/amd64"),
    "amd64": Platform("linux/amd64"),
}
LOCAL_MACHINE_TYPE = platform.machine()
LOCAL_BUILD_PLATFORM = PLATFORM_MACHINE_TO_DAGGER_PLATFORM[LOCAL_MACHINE_TYPE]
AMAZONCORRETTO_IMAGE = "amazoncorretto:21-al2023"
NODE_IMAGE = "node:18.18.0-slim"
GO_IMAGE = "golang:1.17"
PYTHON_3_10_IMAGE = "python:3.10.13-slim"
MAVEN_IMAGE = "maven:3.9.6-amazoncorretto-21-al2023"
DOCKER_VERSION = "24"
DOCKER_DIND_IMAGE = f"docker:{DOCKER_VERSION}-dind"
DOCKER_CLI_IMAGE = f"docker:{DOCKER_VERSION}-cli"
DOCKER_REGISTRY_MIRROR_URL = os.getenv("DOCKER_REGISTRY_MIRROR_URL")
DOCKER_REGISTRY_ADDRESS = "docker.io"
DOCKER_VAR_LIB_VOLUME_NAME = "docker-cache-2"
GIT_IMAGE = "alpine/git:latest"
GIT_DIRECTORY_ROOT_PATH = ".git"
GRADLE_CACHE_PATH = "/root/.gradle/caches"
GRADLE_BUILD_CACHE_PATH = f"{GRADLE_CACHE_PATH}/build-cache-1"
GRADLE_READ_ONLY_DEPENDENCY_CACHE_PATH = "/root/gradle_dependency_cache"
LOCAL_REPORTS_PATH_ROOT = "airbyte-ci/connectors/pipelines/pipeline_reports/"
LOCAL_PIPELINE_PACKAGE_PATH = "airbyte-ci/connectors/pipelines/"
DOCS_DIRECTORY_ROOT_PATH = "docs/"
GCS_PUBLIC_DOMAIN = "https://storage.cloud.google.com"
DOCKER_HOST_NAME = "global-docker-host"
DOCKER_HOST_PORT = 2375
DOCKER_TMP_VOLUME_NAME = "shared-tmp"
STATIC_REPORT_PREFIX = "airbyte-ci"
PIP_CACHE_VOLUME_NAME = "pip_cache"
PIP_CACHE_PATH = "/root/.cache/pip"
POETRY_CACHE_VOLUME_NAME = "poetry_cache"
POETRY_CACHE_PATH = "/root/.cache/pypoetry"
STORAGE_DRIVER = "fuse-overlayfs"
SETUP_PY_FILE_PATH = "setup.py"
DEFAULT_PYTHON_PACKAGE_REGISTRY_URL = "https://upload.pypi.org/legacy/"
DEFAULT_PYTHON_PACKAGE_REGISTRY_CHECK_URL = "https://pypi.org/pypi"
MAIN_CONNECTOR_TESTING_SECRET_STORE_ALIAS = "airbyte-connector-testing-secret-store"
AIRBYTE_SUBMODULE_DIR_NAME = "airbyte-submodule"
MANUAL_PIPELINE_STATUS_CHECK_OVERRIDE_PREFIXES = ["Regression Tests"]

PUBLISH_UPDATES_SLACK_CHANNEL = "#connector-publish-updates"
PUBLISH_FAILURE_SLACK_CHANNEL = "#connector-publish-failures"
# TODO this should be passed via an env var or a CLI input
PATH_TO_LOCAL_CDK = "../airbyte-python-cdk"


class CIContext(str, Enum):
    """An enum for Ci context values which can be ["manual", "pull_request", "nightly_builds"]."""

    MANUAL = "manual"
    PULL_REQUEST = "pull_request"
    MASTER = "master"

    def __str__(self) -> str:
        return self.value


class ContextState(Enum):
    """Enum to characterize the current context state, values are used for external representation on GitHub commit checks."""

    INITIALIZED = {"github_state": "pending", "description": "Pipelines are being initialized..."}
    RUNNING = {"github_state": "pending", "description": "Pipelines are running..."}
    ERROR = {"github_state": "error", "description": "Something went wrong while running the Pipelines."}
    SUCCESSFUL = {"github_state": "success", "description": "All Pipelines ran successfully."}
    FAILURE = {"github_state": "failure", "description": "Pipeline failed."}


class INTERNAL_TOOL_PATHS(str, Enum):
    CI_CREDENTIALS = "airbyte-ci/connectors/ci_credentials"
    CONNECTOR_OPS = "airbyte-ci/connectors/connector_ops"
    CONNECTORS_QA = "airbyte-ci/connectors/connectors_qa"
    METADATA_SERVICE = "airbyte-ci/connectors/metadata_service/lib"


DAGGER_WRAP_ENV_VAR_NAME = "_DAGGER_WRAP_APPLIED"
