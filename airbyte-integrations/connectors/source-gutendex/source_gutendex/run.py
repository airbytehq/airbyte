#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_gutendex import SourceGutendex


def run():
    source = SourceGutendex()
    launch(source, sys.argv[1:])
