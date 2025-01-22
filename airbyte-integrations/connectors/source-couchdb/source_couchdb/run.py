#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch

from .source import SourceCouchdb


def run():
    source = SourceCouchdb()
    launch(source, sys.argv[1:])
