#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_wildberries_ads import SourceWildberriesAds

if __name__ == "__main__":
    source = SourceWildberriesAds()
    launch(source, sys.argv[1:])
