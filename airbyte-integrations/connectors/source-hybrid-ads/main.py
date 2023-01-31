#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_hybrid_ads import SourceHybridAds

if __name__ == "__main__":
    source = SourceHybridAds()
    launch(source, sys.argv[1:])
