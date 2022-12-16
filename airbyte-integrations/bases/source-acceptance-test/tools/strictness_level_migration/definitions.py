#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import yaml

SOURCE_DEFINITIONS_FILE_PATH = "../../../../../airbyte-config/init/src/main/resources/seed/source_definitions.yaml"


def read_source_definitions():
    with open(SOURCE_DEFINITIONS_FILE_PATH, "r") as source_definitions_file:
        return yaml.safe_load(source_definitions_file)


def find_by_release_stage(source_definitions, release_stage):
    return [definition for definition in source_definitions if definition.get("releaseStage") == release_stage]


ALL_DEFINITIONS = read_source_definitions()
GA_DEFINITIONS = find_by_release_stage(ALL_DEFINITIONS, "generally_available")
