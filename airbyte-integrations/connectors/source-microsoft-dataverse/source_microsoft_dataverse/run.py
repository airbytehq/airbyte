#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_microsoft_dataverse import SourceMicrosoftDataverse


def run():
    source = SourceMicrosoftDataverse()
    launch(source, sys.argv[1:])
