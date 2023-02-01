#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Dict, Optional, Set, Tuple, List
import os
import git
import requests
import yaml

# ensure we are at the repository root
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('../../..')

AIRBYTE_REPO = git.Repo(".")
DIFFED_BRANCH = "origin/master"
OSS_CATALOG_URL = "https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/oss_catalog.json"
CONNECTOR_PATH_PREFIX = "airbyte-integrations/connectors"
SOURCE_CONNECTOR_PATH_PREFIX = CONNECTOR_PATH_PREFIX + "/source-"
ACCEPTANCE_TEST_CONFIG_FILE_NAME = "acceptance-test-config.yml"
AIRBYTE_DOCKER_REPO = "airbyte"
SOURCE_DEFINITIONS_FILE_PATH = "airbyte-config/init/src/main/resources/seed/source_definitions.yaml"
DESTINATION_DEFINITIONS_FILE_PATH = "airbyte-config/init/src/main/resources/seed/destination_definitions.yaml"
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
        return yaml.safe_load(definitions_file)

def get_connector_name_from_path(path):
    return path.split("/")[2]


def get_changed_acceptance_test_config(diff_regex: Optional[str]=None) -> Set[str]:
    """Retrieve a list of connector names for which the acceptance_test_config file was changed in the current branch (compared to master).

    Args:
        diff_regex (str): Find the edited files that contain the following regex in their change.

    Returns:
        Set[str]: Set of connector names e.g {"source-pokeapi"}
    """
    if diff_regex is None:
        diff_command_args = ("--name-only", DIFFED_BRANCH)
    else:
        diff_command_args = ("--name-only", f'-G{diff_regex}', DIFFED_BRANCH)

    changed_acceptance_test_config_paths = {
        file_path
        for file_path in AIRBYTE_REPO.git.diff(*diff_command_args).split("\n")
        if file_path.startswith(SOURCE_CONNECTOR_PATH_PREFIX) and file_path.endswith(ACCEPTANCE_TEST_CONFIG_FILE_NAME)
    }
    return {get_connector_name_from_path(changed_file) for changed_file in changed_acceptance_test_config_paths}


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
            return Path(f"./airbyte-config/init/src/main/resources/icons/{self.definition['icon']}")
        return Path(f"./airbyte-config/init/src/main/resources/icons/{self.name}.svg")

    @property
    def code_directory(self) -> Path:
        return Path(f"./airbyte-integrations/connectors/{self.technical_name}")

    @property
    def version(self) -> str:
        with open(self.code_directory / "Dockerfile") as f:
            for line in f:
                if "io.airbyte.version" in line:
                    return line.split("=")[1].strip()
        raise ConnectorVersionNotFound("""
            Could not find the connector version from its Dockerfile.
            The io.airbyte.version tag is missing.
            """)

    @property
    def definition(self) -> Optional[dict]:
        """Find a connector definition from the catalog.
        Returns:
            Optional[Dict]: The definition if the connector was found in the catalog. Returns None otherwise.
        """
        try:
            definition_type = self.technical_name.split("-")[0]
            assert definition_type in ["source", "destination"]
        except AssertionError:
            raise Exception(f"Could not determine the definition type for {self.technical_name}.")
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

    def __repr__(self) -> str:
        return self.technical_name

def get_changed_connectors() -> Set[Connector]:
    """Retrieve a list of Connectors that were changed in the current branch (compared to master).
    """
    changed_source_connector_files = {
        file_path
        for file_path in AIRBYTE_REPO.git.diff("--name-only", DIFFED_BRANCH).split("\n")
        if file_path.startswith(SOURCE_CONNECTOR_PATH_PREFIX)
    }
    return {Connector(get_connector_name_from_path(changed_file)) for changed_file in changed_source_connector_files}
