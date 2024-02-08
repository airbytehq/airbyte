#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_emailoctopus import SourceEmailoctopus


def run():
    source = SourceEmailoctopus()
    launch(source, sys.argv[1:])
