#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_wikipedia_pageviews import SourceWikipediaPageviews

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceWikipediaPageviews()
    launch(source, sys.argv[1:])
