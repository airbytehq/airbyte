#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_secoda import SourceSecoda


def run():
    source = SourceSecoda()
    launch(source, sys.argv[1:])
