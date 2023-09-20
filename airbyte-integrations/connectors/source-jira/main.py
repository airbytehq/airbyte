#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_jira import SourceJira
from source_jira.config_migrations import MigrateIssueExpandProperties

if __name__ == "__main__":
    source = SourceJira()
    MigrateIssueExpandProperties.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
