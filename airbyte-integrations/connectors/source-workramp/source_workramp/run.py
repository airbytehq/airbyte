#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_workramp import SourceWorkramp


def run():
    source = SourceWorkramp()
    launch(source, sys.argv[1:])
