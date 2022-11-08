#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from pathlib import Path

from config_migration import migrate_to_high_test_strictness_level
from definitions import GA_DEFINITIONS
from git import Repo

CONNECTORS_DIRECTORY = "../../../../connectors"
REPO_ROOT = "../../../../../"

repo = Repo(REPO_ROOT)


def migrate_acceptance_test_config(definition):
    connector_name = definition["dockerRepository"].replace("airbyte/", "")
    acceptance_test_config_path = Path(CONNECTORS_DIRECTORY) / connector_name / "acceptance-test-config.yml"
    migrate_to_high_test_strictness_level(acceptance_test_config_path)


migrate_acceptance_test_config(GA_DEFINITIONS[5])
