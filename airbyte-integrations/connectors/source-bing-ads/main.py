#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_bing_ads import SourceBingAds

if __name__ == "__main__":
    source = SourceBingAds()
    launch(source, sys.argv[1:])
