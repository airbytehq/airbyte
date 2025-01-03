#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_braze import SourceBraze

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceBraze()
    launch(source, sys.argv[1:])
