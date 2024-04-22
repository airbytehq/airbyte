#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_ashby import SourceAshby


def run():
    source = SourceAshby()
    launch(source, sys.argv[1:])
