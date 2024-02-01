#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_serpstat import SourceSerpstat


def run():
    source = SourceSerpstat()
    launch(source, sys.argv[1:])
