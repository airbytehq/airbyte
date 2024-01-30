#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_commcare import SourceCommcare


def run():
    source = SourceCommcare()
    launch(source, sys.argv[1:])
