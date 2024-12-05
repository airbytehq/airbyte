#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_monday import SourceMonday


def run():
    source = SourceMonday()
    launch(source, sys.argv[1:])
