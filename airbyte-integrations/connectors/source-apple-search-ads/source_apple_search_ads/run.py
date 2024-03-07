#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_apple_search_ads import SourceAppleSearchAds


def run():
    source = SourceAppleSearchAds()
    launch(source, sys.argv[1:])
