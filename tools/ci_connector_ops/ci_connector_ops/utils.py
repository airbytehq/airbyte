#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import git
import requests
import yaml
from ci_credentials import SecretsManager
from rich.console import Console

try:
    from yaml import CLoader as Loader
# Some environments do not have a system C Yaml loader
except ImportError:
    from yaml import Loader

console = Console()

DIFFED_BRANCH = os.environ.get("DIFFED_BRANCH", "origin/master")
OSS_CATALOG_URL = "https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/oss_catalog.json"
CONNECTOR_PATH_PREFIX = "airbyte-integrations/connectors"
SOURCE_CONNECTOR_PATH_PREFIX = CONNECTOR_PATH_PREFIX + "/source-"
DESTINATION_CONNECTOR_PATH_PREFIX = CONNECTOR_PATH_PREFIX + "/destination-"
ACCEPTANCE_TEST_CONFIG_FILE_NAME = "acceptance-test-config.yml"
AIRBYTE_DOCKER_REPO = "airbyte"
SOURCE_DEFINITIONS_FILE_PATH = "airbyte-config-oss/init-oss/src/main/resources/seed/source_definitions.yaml"
DESTINATION_DEFINITIONS_FILE_PATH = "airbyte-config-oss/init-oss/src/main/resources/seed/destination_definitions.yaml"
DEFINITIONS_FILE_PATH = {"source": SOURCE_DEFINITIONS_FILE_PATH, "destination": DESTINATION_DEFINITIONS_FILE_PATH}


def download_catalog(catalog_url):
    response = requests.get(catalog_url)
    return response.json()


OSS_CATALOG = download_catalog(OSS_CATALOG_URL)


class ConnectorInvalidNameError(Exception):
    pass


class ConnectorVersionNotFound(Exception):
    pass


def read_definitions(definitions_file_path: str) -> Dict:
    with open(definitions_file_path) as definitions_file:
        return yaml.load(definitions_file, Loader=Loader)


def get_connector_name_from_path(path):
    return path.split("/")[2]


def get_changed_acceptance_test_config(diff_regex: Optional[str] = None) -> Set[str]:
    """Retrieve the set of connectors for which the acceptance_test_config file was changed in the current branch (compared to master).

    Args:
        diff_regex (str): Find the edited files that contain the following regex in their change.

    Returns:
        Set[Connector]: Set of connectors that were changed
    """
    airbyte_repo = git.Repo(search_parent_directories=True)

    if diff_regex is None:
        diff_command_args = ("--name-only", DIFFED_BRANCH)
    else:
        diff_command_args = ("--name-only", f"-G{diff_regex}", DIFFED_BRANCH)

    changed_acceptance_test_config_paths = {
        file_path
        for file_path in airbyte_repo.git.diff(*diff_command_args).split("\n")
        if file_path.startswith(SOURCE_CONNECTOR_PATH_PREFIX) and file_path.endswith(ACCEPTANCE_TEST_CONFIG_FILE_NAME)
    }
    return {Connector(get_connector_name_from_path(changed_file)) for changed_file in changed_acceptance_test_config_paths}


class ConnectorLanguage(str, Enum):
    PYTHON = "python"
    JAVA = "java"
    LOW_CODE = "low-code"


class ConnectorLanguageError(Exception):
    pass


@dataclass(frozen=True)
class Connector:
    """Utility class to gather metadata about a connector."""

    technical_name: str

    def _get_type_and_name_from_technical_name(self) -> Tuple[str, str]:
        if "-" not in self.technical_name:
            raise ConnectorInvalidNameError(f"Connector type and name could not be inferred from {self.technical_name}")
        _type = self.technical_name.split("-")[0]
        name = self.technical_name[len(_type) + 1 :]
        return _type, name

    @property
    def name(self):
        return self._get_type_and_name_from_technical_name()[1]

    @property
    def connector_type(self) -> str:
        return self._get_type_and_name_from_technical_name()[0]

    @property
    def documentation_file_path(self) -> Path:
        return Path(f"./docs/integrations/{self.connector_type}s/{self.name}.md")

    @property
    def icon_path(self) -> Path:
        if self.definition and self.definition.get("icon"):
            return Path(f"./airbyte-config-oss/init-oss/src/main/resources/icons/{self.definition['icon']}")
        return Path(f"./airbyte-config-oss/init-oss/src/main/resources/icons/{self.name}.svg")

    @property
    def code_directory(self) -> Path:
        return Path(f"./airbyte-integrations/connectors/{self.technical_name}")

    @property
    def language(self) -> ConnectorLanguage:
        if Path(self.code_directory / self.technical_name.replace("-", "_") / "manifest.yaml").is_file():
            return ConnectorLanguage.LOW_CODE
        if Path(self.code_directory / "setup.py").is_file():
            return ConnectorLanguage.PYTHON
        try:
            with open(self.code_directory / "Dockerfile") as dockerfile:
                if "FROM airbyte/integration-base-java" in dockerfile.read():
                    return ConnectorLanguage.JAVA
        except FileNotFoundError:
            pass
        return None
        # raise ConnectorLanguageError(f"We could not infer {self.technical_name} connector language")

    @property
    def version(self) -> str:
        with open(self.code_directory / "Dockerfile") as f:
            for line in f:
                if "io.airbyte.version" in line:
                    return line.split("=")[1].strip()
        raise ConnectorVersionNotFound(
            """
            Could not find the connector version from its Dockerfile.
            The io.airbyte.version tag is missing.
            """
        )

    @cached_property
    def definition(self) -> Optional[dict]:
        """Find a connector definition from the catalog.
        Returns:
            Optional[Dict]: The definition if the connector was found in the catalog. Returns None otherwise.
        """
        try:
            definition_type = self.technical_name.split("-")[0]
            assert definition_type in ["source", "destination"]
        except AssertionError:
            return None
        definitions = read_definitions(DEFINITIONS_FILE_PATH[definition_type])
        for definition in definitions:
            if definition["dockerRepository"].replace(f"{AIRBYTE_DOCKER_REPO}/", "") == self.technical_name:
                return definition

    @property
    def release_stage(self) -> Optional[str]:
        return self.definition.get("releaseStage") if self.definition else None

    @property
    def allowed_hosts(self) -> Optional[List[str]]:
        return self.definition.get("allowedHosts") if self.definition else None

    @property
    def suggested_streams(self) -> Optional[List[str]]:
        return self.definition.get("suggestedStreams") if self.definition else None

    @property
    def acceptance_test_config_path(self) -> Path:
        return self.code_directory / ACCEPTANCE_TEST_CONFIG_FILE_NAME

    @property
    def acceptance_test_config(self) -> Optional[dict]:
        try:
            with open(self.acceptance_test_config_path) as acceptance_test_config_file:
                return yaml.safe_load(acceptance_test_config_file)
        except FileNotFoundError:
            logging.warning(f"No {ACCEPTANCE_TEST_CONFIG_FILE_NAME} file found for {self.technical_name}")
            return None

    @property
    def supports_normalization(self) -> bool:
        return self.definition and self.definition.get("normalizationConfig") is not None

    @property
    def normalization_repository(self) -> Optional[str]:
        if self.supports_normalization:
            return f"{self.definition['normalizationConfig']['normalizationRepository']}"

    @property
    def normalization_tag(self) -> Optional[str]:
        if self.supports_normalization:
            return f"{self.definition['normalizationConfig']['normalizationTag']}"

    def get_secret_manager(self, gsm_credentials: str):
        return SecretsManager(connector_name=self.technical_name, gsm_credentials=gsm_credentials)

    def __repr__(self) -> str:
        return self.technical_name


def get_changed_connectors() -> Set[Connector]:
    """Retrieve a set of Connectors that were changed in the current branch (compared to master)."""
    airbyte_repo = git.Repo(search_parent_directories=True)
    changed_source_connector_files = {
        file_path
        for file_path in airbyte_repo.git.diff("--name-only", DIFFED_BRANCH).split("\n")
        if file_path.startswith(SOURCE_CONNECTOR_PATH_PREFIX)
    }
    return {Connector(get_connector_name_from_path(changed_file)) for changed_file in changed_source_connector_files}


def get_all_released_connectors() -> Set:
    all_definitions = OSS_CATALOG["sources"] + OSS_CATALOG["destinations"]
    return {Connector(definition["dockerRepository"].replace("airbyte/", "")) for definition in all_definitions}
