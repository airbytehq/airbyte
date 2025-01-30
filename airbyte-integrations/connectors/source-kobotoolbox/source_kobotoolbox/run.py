#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .source import SourceKobotoolbox

def run():
    source = SourceKobotoolbox()
    launch(source, sys.argv[1:])
