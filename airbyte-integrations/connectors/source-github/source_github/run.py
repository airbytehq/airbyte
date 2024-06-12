#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_github import SourceGithub
from source_github.config_migrations import MigrateBranch, MigrateRepository


def run():
    source = SourceGithub()
    MigrateRepository.migrate(sys.argv[1:], source)
    MigrateBranch.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
