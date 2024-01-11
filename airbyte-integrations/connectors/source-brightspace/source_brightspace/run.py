#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .source import SourceBrightspace

def run():
    source = SourceBrightspace()
    launch(source, sys.argv[1:])
