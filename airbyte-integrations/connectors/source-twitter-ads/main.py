#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_twitter_ads import SourceTwitterAds

if __name__ == "__main__":
    source = SourceTwitterAds()
    launch(source, sys.argv[1:])
