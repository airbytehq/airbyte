#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_amazon_ads import SourceAmazonAds

if __name__ == "__main__":
    source = SourceAmazonAds()
    launch(source, sys.argv[1:])
