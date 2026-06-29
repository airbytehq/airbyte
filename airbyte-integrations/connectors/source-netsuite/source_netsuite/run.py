#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging

logging.basicConfig(level=logging.DEBUG)

# Enable debugging for requests and underlying HTTP connections
logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

import sys

from airbyte_cdk.entrypoint import launch

from .source import SourceNetsuite


def run():
    source = SourceNetsuite()
    launch(source, sys.argv[1:])
