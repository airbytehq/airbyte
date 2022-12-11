#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_wikipedia_pageviews import SourceWikipediaPageviews

if __name__ == "__main__":
    source = SourceWikipediaPageviews()
    launch(source, sys.argv[1:])
