#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_jira import SourceJira


def run():
    source = SourceJira()
    launch(source, sys.argv[1:])
