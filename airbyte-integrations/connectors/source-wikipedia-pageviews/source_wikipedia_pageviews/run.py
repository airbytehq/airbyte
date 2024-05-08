#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_wikipedia_pageviews import SourceWikipediaPageviews


def run():
    source = SourceWikipediaPageviews()
    launch(source, sys.argv[1:])
