#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_intruder import SourceIntruder


def run():
    source = SourceIntruder()
    launch(source, sys.argv[1:])
