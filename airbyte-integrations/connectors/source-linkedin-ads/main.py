#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_linkedin_ads import SourceLinkedinAds

if __name__ == "__main__":
    source = SourceLinkedinAds()
    launch(source, sys.argv[1:])
