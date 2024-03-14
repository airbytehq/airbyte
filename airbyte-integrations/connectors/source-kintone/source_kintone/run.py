#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .source import SourceKintone

def run():
    source = SourceKintone()
    launch(source, sys.argv[1:])
