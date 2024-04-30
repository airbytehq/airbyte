#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_gitlab import SourceGitlab
from source_gitlab.config_migrations import MigrateGroups, MigrateProjects


def run():
    source = SourceGitlab()
    MigrateGroups.migrate(sys.argv[1:], source)
    MigrateProjects.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
