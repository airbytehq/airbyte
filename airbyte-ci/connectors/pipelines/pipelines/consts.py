#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import platform
from enum import Enum

import git
from dagger import Platform

PYPROJECT_TOML_FILE_PATH = "pyproject.toml"
LICENSE_SHORT_FILE_PATH = "LICENSE_SHORT"
CONNECTOR_TESTING_REQUIREMENTS = [
    "pip==21.3.1",
    "mccabe==0.6.1",
    "flake8==4.0.1",
    "pyproject-flake8==0.0.1a2",
    "black==22.3.0",
    "isort==5.6.4",
    "pytest==6.2.5",
    "coverage[toml]==6.3.1",
    "pytest-custom_exit_code",
    "licenseheaders==0.8.8",
]

BUILD_PLATFORMS = [Platform("linux/amd64"), Platform("linux/arm64")]

PLATFORM_MACHINE_TO_DAGGER_PLATFORM = {
    "x86_64": Platform("linux/amd64"),
    "arm64": Platform("linux/arm64"),
    "amd64": Platform("linux/amd64"),
}
LOCAL_BUILD_PLATFORM = PLATFORM_MACHINE_TO_DAGGER_PLATFORM[platform.machine()]
AMAZONCORRETTO_IMAGE = "amazoncorretto:17.0.8-al2023"
DOCKER_VERSION = "24.0.2"
DOCKER_DIND_IMAGE = f"docker:{DOCKER_VERSION}-dind"
DOCKER_CLI_IMAGE = f"docker:{DOCKER_VERSION}-cli"
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
DOCKER_VAR_LIB_VOLUME_NAME = "docker-cache"
REPO = git.Repo(search_parent_directories=True)
REPO_PATH = REPO.working_tree_dir
STATIC_REPORT_PREFIX = "airbyte-ci"
PIP_CACHE_VOLUME_NAME = "pip_cache"
PIP_CACHE_PATH = "/root/.cache/pip"
POETRY_CACHE_VOLUME_NAME = "poetry_cache"
POETRY_CACHE_PATH = "/root/.cache/pypoetry"


class CIContext(str, Enum):
    """An enum for Ci context values which can be ["manual", "pull_request", "nightly_builds"]."""

    MANUAL = "manual"
    PULL_REQUEST = "pull_request"
    NIGHTLY_BUILDS = "nightly_builds"
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
    METADATA_SERVICE = "airbyte-ci/connectors/metadata_service/lib"
