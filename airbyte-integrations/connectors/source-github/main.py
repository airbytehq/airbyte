#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_github import SourceGithub
from source_github.config_migrations import MigrateBranch, MigrateRepository

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceGithub()
    MigrateRepository.migrate(sys.argv[1:], source)
    MigrateBranch.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
