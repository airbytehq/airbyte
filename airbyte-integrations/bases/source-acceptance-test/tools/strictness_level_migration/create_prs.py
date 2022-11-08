#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from pathlib import Path

from config_migration import migrate_to_high_test_strictness_level
from definitions import GA_DEFINITIONS
from git import Repo

CONNECTORS_DIRECTORY = "../../../../connectors"
REPO_ROOT = "../../../../../"


def migrate_acceptance_test_config(connector_name):
    acceptance_test_config_path = Path(CONNECTORS_DIRECTORY) / connector_name / "acceptance-test-config.yml"
    return migrate_to_high_test_strictness_level(acceptance_test_config_path)


def main():
    airbyte_repo = Repo(REPO_ROOT)
    original_branch = airbyte_repo.active_branch
    definition = GA_DEFINITIONS[5]
    connector_name = definition["dockerRepository"].replace("airbyte/", "")
    new_branch_name = f"{connector_name}/sat/migrate-to-high-test-strictness-level"
    new_branch = airbyte_repo.create_head(new_branch_name)
    new_branch.checkout()
    migrate_acceptance_test_config(connector_name)
    relative_config_path = f"airbyte-integrations/connectors/{connector_name}/acceptance-test-config.yml"
    airbyte_repo.git.add(relative_config_path)
    airbyte_repo.git.commit(m=f"Migrated config for {connector_name}")
    airbyte_repo.git.push("--set-upstream", "origin", new_branch)
    original_branch.checkout()


main()
