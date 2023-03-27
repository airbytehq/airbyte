#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import argparse
import logging
from pathlib import Path

import utils
from connector_acceptance_test.config import Config
from definitions import BETA_DEFINITIONS, GA_DEFINITIONS, get_airbyte_connector_name_from_definition, is_airbyte_connector
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 150

parser = argparse.ArgumentParser(description="Migrate legacy acceptance-test-config.yml to the latest configuration format.")
parser.add_argument("--connectors", nargs="*")
parser.add_argument("--allow_alpha", action=argparse.BooleanOptionalAction, default=False)


def load_config(config_path: Path) -> Config:
    with open(config_path, "r") as file:
        config = yaml.load(file)
    return config


def migrate_to_new_config_format(config: Config):
    if Config.is_legacy(config):
        return Config.migrate_legacy_to_current_config(config)
    else:
        logging.warning("The configuration is not in a legacy format.")
        return config


def set_high_test_strictness_level(config):
    if Config.is_legacy(config):
        raise Exception("You can't set a strictness level on a legacy config.")
    config["test_strictness_level"] = "high"
    for basic_read_test in config["acceptance_tests"].get("basic_read", {"tests": []})["tests"]:
        basic_read_test.pop("configured_catalog_path", None)
    return config


def set_ignore_extra_columns(config):
    if Config.is_legacy(config):
        for basic_read_test in config["tests"].get("basic_read"):
            basic_read_test["fail_on_extra_columns"] = False
    else:
        for basic_read_test in config["acceptance_tests"].get("basic_read", {"tests": []})["tests"]:
            basic_read_test["fail_on_extra_columns"] = False
    return config


def write_new_config(new_config, output_path):
    with open(output_path, "w") as output_file:
        yaml.dump(new_config, output_file)
    logging.info("Saved the configuration in its new format")


def update_configuration(config_path):
    old_config = load_config(config_path)
    # migrated_config = migrate_to_new_config_format(old_config)
    new_config = set_ignore_extra_columns(old_config)
    write_new_config(new_config, config_path)
    logging.info(f"The configuration was successfully updated: {config_path}")
    return config_path


if __name__ == "__main__":
    args = parser.parse_args()
    definitions = utils.get_definitions_from_args(args)

    for definition in definitions:
        if not is_airbyte_connector(definition):
            logging.error(f"Couldn't create PR for non-airbyte connector: {definition.get('dockerRepository')}")
        if not args.allow_alpha and definition not in BETA_DEFINITIONS + GA_DEFINITIONS:
            logging.info(f"Not updating {get_airbyte_connector_name_from_definition} because it's not GA or Beta.")
        else:
            config_path = utils.acceptance_test_config_path(get_airbyte_connector_name_from_definition)
            update_configuration(config_path)
