#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_nasa import SourceNasa


def run():
    source = SourceNasa()
    launch(source, sys.argv[1:])
