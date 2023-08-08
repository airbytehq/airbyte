#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import List

import requests

logging.basicConfig(level=logging.DEBUG)

CONNECTOR_REGISTRY_URL = "https://connectors.airbyte.com/files/registries/v0/oss_registry.json"


def download_and_parse_registry_json():
    response = requests.get(CONNECTOR_REGISTRY_URL)
    response.raise_for_status()
    return response.json()


def read_source_definitions():
    return download_and_parse_registry_json()["sources"]


def find_by_support_level(source_definitions, support_level):
    if support_level == "other":
        return [definition for definition in source_definitions if definition.get("supportLevel", "") not in ["community", "certified"]]
    else:
        return [definition for definition in source_definitions if definition.get("supportLevel") == support_level]


def find_by_name(connector_names: List[str]):
    definitions = [
        definition for definition in ALL_DEFINITIONS if get_airbyte_connector_name_from_definition(definition) in connector_names
    ]
    if len(definitions) != len(connector_names):
        logging.warning(f"Looked for {len(connector_names)} items, got {len(definitions)} items. Did you misspell something?")
    return definitions


def get_airbyte_connector_name_from_definition(connector_definition):
    return connector_definition["dockerRepository"].replace("airbyte/", "")


def is_airbyte_connector(connector_definition):
    return connector_definition["dockerRepository"].startswith("airbyte/")


ALL_DEFINITIONS = read_source_definitions()
CERTIFIED_DEFINITIONS = find_by_support_level(ALL_DEFINITIONS, "certified")
COMMUNITY_DEFINITIONS = find_by_support_level(ALL_DEFINITIONS, "community")
OTHER_DEFINITIONS = find_by_support_level(ALL_DEFINITIONS, "other")
