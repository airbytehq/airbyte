#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import argparse
import logging
from pathlib import Path
from typing import Callable

import definitions
import utils
from connector_acceptance_test.config import Config
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 150

parser = argparse.ArgumentParser(description="Migrate acceptance-test-config.yml files for a list of connectors.")
utils.add_connectors_param(parser)
utils.add_allow_alpha_param(parser)
utils.add_allow_beta_param(parser)
parser.add_argument(
    "--migrate_from_legacy",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="Whether to migrate config files from the legacy format before applying the migration.",
)


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
        raise Exception("You can't set a strictness level on a legacy config. Please use the `--migrate_from_legacy` flag.")
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


def update_configuration(config_path, migration: Callable, migrate_from_legacy: bool):
    config_to_migrate = load_config(config_path)
    if migrate_from_legacy:
        config_to_migrate = migrate_to_new_config_format(config_to_migrate)
    new_config = migration(config_to_migrate)
    write_new_config(new_config, config_path)
    logging.info(f"The configuration was successfully updated: {config_path}")
    return config_path


if __name__ == "__main__":
    args = parser.parse_args()

    # Update this before running the script
    MIGRATION_TO_RUN = set_high_test_strictness_level

    for definition in utils.get_valid_definitions_from_args(args):
        config_path = utils.acceptance_test_config_path(definitions.get_airbyte_connector_name_from_definition(definition))
        update_configuration(config_path, MIGRATION_TO_RUN, args.migrate_from_legacy)
