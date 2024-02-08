#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_dremio import SourceDremio


def run():
    source = SourceDremio()
    launch(source, sys.argv[1:])
