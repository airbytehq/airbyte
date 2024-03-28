#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .source import SourceZenoti

def run():
    source = SourceZenoti()
    launch(source, sys.argv[1:])
