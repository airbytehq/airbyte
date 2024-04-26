#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_iterable import SourceIterable


def run():
    source = SourceIterable()
    launch(source, sys.argv[1:])
