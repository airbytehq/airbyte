#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_jira import SourceJira

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceJira()
    launch(source, sys.argv[1:])
