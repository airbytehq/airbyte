#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from .source import SourceWebsiteScraper


def run():
    source = SourceWebsiteScraper()
    launch(source, sys.argv[1:])
