#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_jira import SourceJira

if __name__ == "__main__":
    source = SourceJira()
    launch(source, sys.argv[1:])
