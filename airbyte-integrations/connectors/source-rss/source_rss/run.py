#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_rss import SourceRss

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceRss()
    launch(source, sys.argv[1:])
