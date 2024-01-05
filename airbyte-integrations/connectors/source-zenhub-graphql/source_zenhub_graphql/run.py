#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
import logging

from airbyte_cdk.entrypoint import launch
from .source import SourceZenhubGraphql

def run():
    logging.basicConfig(level=logging.INFO)
    logging.info("TESTING INTERESTING")
    source = SourceZenhubGraphql()
    launch(source, sys.argv[1:])
