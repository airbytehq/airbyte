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


def migrate_legacy_configuration(config_path: Path):

    with open(config_path, "r") as file:
        to_migrate = load(file, Loader=Loader)

    if Config.is_legacy(to_migrate):
        new_config = Config.migrate_legacy_to_current_config(to_migrate)
        logging.info(f"Your configuration was successfully migrated to the latest configuration format: {config_path}")
        return new_config
    else:
        logging.warning("Your configuration is not in a legacy format.")
        return None


def set_high_test_strictness_level(configuration):
    configuration["test_strictness_level"] = "high"
    for basic_read_test in configuration["acceptance_tests"]["basic_read"]["tests"]:
        if "configured_catalog_path" in basic_read_test:
            basic_read_test.pop("configured_catalog_path")
    return configuration


def write_new_config(new_configuration, output_path):
    with open(output_path, "w") as output_file:
        yaml.dump(new_configuration, output_file)
    logging.info(f"Your configuration was successfully migrated to the latest configuration format: {output_path}")


def migrate_to_high_test_strictness_level(config_path):
    new_config = migrate_legacy_configuration(config_path)
    new_config = set_high_test_strictness_level(new_config)
    write_new_config(new_config, config_path)


if __name__ == "__main__":
    args = parser.parse_args()
    migrate_to_high_test_strictness_level(Path(args.config_path))
