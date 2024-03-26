#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_dixa import SourceDixa


def run():
    source = SourceDixa()
    launch(source, sys.argv[1:])
