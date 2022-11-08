#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import argparse
import logging
from pathlib import Path

import yaml
from source_acceptance_test.config import Config
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

parser = argparse.ArgumentParser(description="Migrate legacy acceptance-test-config.yml to the latest configuration format.")
parser.add_argument("config_path", type=str, help="Path to the acceptance-test-config.yml to migrate.")


def get_new_config_format(config_path: Path):

    with open(config_path, "r") as file:
        to_migrate = load(file, Loader=Loader)

    if Config.is_legacy(to_migrate):
        return Config.migrate_legacy_to_current_config(to_migrate)
    else:
        logging.warn("The configuration is not in a legacy format.")
        return to_migrate


def set_high_test_strictness_level(config):
    config["test_strictness_level"] = "high"
    for basic_read_test in config["acceptance_tests"].get("basic_read", {"tests": []})["tests"]:
        basic_read_test.pop("configured_catalog_path", None)
    return config


def write_new_config(new_config, output_path):
    with open(output_path, "w") as output_file:
        yaml.dump(new_config, output_file)
    logging.info("Saved the configuration in its new format")


def migrate_configuration(config_path):
    new_config = get_new_config_format(config_path)
    new_config = set_high_test_strictness_level(new_config)
    write_new_config(new_config, config_path)
    logging.info(f"The configuration was successfully migrated to the latest configuration format: {config_path}")
    return config_path


if __name__ == "__main__":
    args = parser.parse_args()
    config_path = Path(args.config_path)
    migrate_configuration(config_path)
