#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_notion import SourceNotion


def run():
    source = SourceNotion()
    launch(source, sys.argv[1:])
