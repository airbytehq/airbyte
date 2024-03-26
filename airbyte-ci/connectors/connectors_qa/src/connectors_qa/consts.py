# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from base_images.python.bases import AirbytePythonConnectorBaseImage  # type: ignore

CONNECTORS_QA_DOC_TEMPLATE_NAME = "qa_checks.md.j2"
DOCKER_HUB_PASSWORD_ENV_VAR_NAME = "DOCKER_HUB_PASSWORD"
DOCKER_HUB_USERNAME_ENV_VAR_NAME = "DOCKER_HUB_USERNAME"
DOCKER_INDEX = "docker.io"
DOCKERFILE_NAME = "Dockerfile"
DOCUMENTATION_STANDARDS_URL = "https://hackmd.io/Bz75cgATSbm7DjrAqgl4rw"
GRADLE_FILE_NAME = "build.gradle"
LICENSE_FAQ_URL = "https://docs.airbyte.com/developer-guides/licenses/license-faq"
LOW_CODE_MANIFEST_FILE_NAME = "manifest.yaml"
METADATA_DOCUMENTATION_URL = "https://docs.airbyte.com/connector-development/connector-metadata-file"
METADATA_FILE_NAME = "metadata.yaml"
POETRY_LOCK_FILE_NAME = "poetry.lock"
PYPROJECT_FILE_NAME = "pyproject.toml"
SEMVER_FOR_CONNECTORS_DOC_URL = "https://docs.airbyte.com/contributing-to-airbyte/#semantic-versioning-for-connectors"
SETUP_PY_FILE_NAME = "setup.py"
VALID_LICENSES = {"MIT", "ELV2"}

# Derived from other constants
AIRBYTE_PYTHON_CONNECTOR_BASE_IMAGE_NAME = f"{DOCKER_INDEX}/{AirbytePythonConnectorBaseImage.repository}"
