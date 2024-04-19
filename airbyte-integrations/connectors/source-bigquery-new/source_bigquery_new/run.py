#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .source import SourceBigqueryNew

def run():
    source = SourceBigqueryNew()
    launch(source, sys.argv[1:])
