#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_linkedin_ads import SourceLinkedinAds

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceLinkedinAds()
    launch(source, sys.argv[1:])
