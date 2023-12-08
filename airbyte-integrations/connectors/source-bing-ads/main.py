#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_bing_ads import SourceBingAds

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceBingAds()
    launch(source, sys.argv[1:])
