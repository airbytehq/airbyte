#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Dict, Optional, Set, Tuple

import git
import requests
import yaml

AIRBYTE_REPO = git.Repo(".")
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


class ConnectorNotFoundError(Exception):
    pass


def read_definitions(definitions_file_path: str) -> Dict:
    with open(definitions_file_path) as definitions_file:
        return yaml.safe_load(definitions_file)

def get_connector_name_from_path(path):
    return path.split("/")[2]

def get_changed_connector_names() -> Set[str]:
    """Retrieve a list of connector names that were changed in the current branch (compared to master).

    Returns:
        Set[str]: Set of connector names e.g ["source-pokeapi"]
    """
    changed_source_connector_files = {
        file_path
        for file_path in AIRBYTE_REPO.git.diff("--name-only", "origin/master").split("\n")
        if file_path.startswith(SOURCE_CONNECTOR_PATH_PREFIX)
    }

    return {get_connector_name_from_path(changed_file) for changed_file in changed_source_connector_files}

def get_changed_acceptance_test_config(diff_regex: Optional[str]=None) -> Set[str]:
    """Retrieve a list of connector names for which the acceptance_test_config file was changed in the current branch (compared to master).

    Args:
        diff_regex (str): Find the edited files that contain the following regex in their change.

    Returns:
        Set[str]: Set of connector names e.g {"source-pokeapi"}
    """
    if diff_regex is None:
        diff_command_args = ("--name-only", "origin/master")
    else:
        diff_command_args = ("--name-only", f'-G{diff_regex}', "origin/master")

    changed_acceptance_test_config_paths = {
        file_path
        for file_path in AIRBYTE_REPO.git.diff(*diff_command_args).split("\n")
        if file_path.startswith(SOURCE_CONNECTOR_PATH_PREFIX) and file_path.endswith(ACCEPTANCE_TEST_CONFIG_FILE_NAME)
    }
    return {get_connector_name_from_path(changed_file) for changed_file in changed_acceptance_test_config_paths}

def get_connector_definition(connector_name: str) -> Optional[Dict]:
    """Find a connector definition from the catalog.

    Args:
        connector_name (str): The connector name. E.G. 'source-pokeapi'

    Raises:
        Exception: Raised if the definition type (source/destination) could not be determined from connector name.

    Returns:
        Optional[Dict]: The definition if the connector was found in the catalo. Returns None otherwise.
    """
    try:
        definition_type = connector_name.split("-")[0]
        assert definition_type in ["source", "destination"]
    except AssertionError:
        raise Exception(f"Could not determine the definition type for {connector_name}.")
    definitions = read_definitions(DEFINITIONS_FILE_PATH[definition_type])
    for definition in definitions:
        if definition["dockerRepository"].replace(f"{AIRBYTE_DOCKER_REPO}/", "") == connector_name:
            return definition
    raise ConnectorNotFoundError(f"{connector_name} was not found in {DEFINITIONS_FILE_PATH[definition_type]}")


def get_connector_release_stage(connector_name: str) -> Optional[str]:
    """Retrieve the connector release stage (E.G. alpha/beta/generally_available).

    Args:
        connector_name (str): The connector name. E.G. 'source-pokeapi'

    Returns:
        Optional[str]: The connector release stage if it was defined. Returns None otherwise.
    """
    try:
        definition = get_connector_definition(connector_name)
        return definition.get("releaseStage")
    except ConnectorNotFoundError as e:
        logging.warning(str(e))


def get_acceptance_test_config(connector_name: str) -> Tuple[str, Dict]:
    """Retrieve the acceptance test config file path and its content as dict.

    Args:
        connector_name (str): The connector name. E.G. 'source-pokeapi'


    Returns:
        Tuple(str, Dict): The acceptance test config file path and its content as dict.
    """
    acceptance_test_config_path = f"{CONNECTOR_PATH_PREFIX}/{connector_name}/{ACCEPTANCE_TEST_CONFIG_FILE_NAME}"
    try:
        with open(acceptance_test_config_path) as acceptance_test_config_file:
            return acceptance_test_config_path, yaml.safe_load(acceptance_test_config_file)
    except FileNotFoundError:
        logging.warning(f"No {ACCEPTANCE_TEST_CONFIG_FILE_NAME} file found for {connector_name}")
        return None, None

@dataclass
class Connector:
    # TODO a couple of functions defined at the root level of this module can be moved into this class.
    """Utility class to gather metadata about a connector."""
    connector_technical_name: str

    def _get_type_and_name_from_technical_name(self) -> Tuple[str, str]:
        _type = self.connector_technical_name.split("-")[0]
        name = self.connector_technical_name[len(_type) + 1 :]
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
        if self.definition.get("icon"):
            return Path(f"./airbyte-config/init/src/main/resources/icons/{self.definition['icon']}")
        return Path(f"./airbyte-config/init/src/main/resources/icons/{self.name}.svg")

    @property
    def code_directory(self) -> Path:
        return Path(f"./airbyte-integrations/connectors/{self.connector_technical_name}")
    
    @property
    def version(self) -> str:
        with open(self.code_directory / "Dockerfile") as f:
            for line in f:
                if "io.airbyte.version" in line:
                    return line.split("=")[1].strip()
        raise Exception("Could not find the connector version from its Dockerfile")

    @property
    def definition(self) -> Optional[dict]:
        return get_connector_definition(self.connector_technical_name)
