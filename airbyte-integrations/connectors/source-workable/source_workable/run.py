#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_workable import SourceWorkable


def run():
    source = SourceWorkable()
    launch(source, sys.argv[1:])
