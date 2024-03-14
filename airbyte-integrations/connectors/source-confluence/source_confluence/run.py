#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_confluence import SourceConfluence


def run():
    source = SourceConfluence()
    launch(source, sys.argv[1:])
