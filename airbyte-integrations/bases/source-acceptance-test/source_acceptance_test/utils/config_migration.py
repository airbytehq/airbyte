#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import argparse
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
        migrated_config = Config.migrate_legacy_to_current_config(to_migrate)
        with open(config_path, "w") as output_file:
            yaml.dump(migrated_config, output_file)
        print(f"Your configuration was successfully migrated to the latest configuration format: {config_path}")
    else:
        print("Your configuration is not in a legacy format.")


if __name__ == "__main__":
    args = parser.parse_args()
    migrate_legacy_configuration(Path(args.config_path))
