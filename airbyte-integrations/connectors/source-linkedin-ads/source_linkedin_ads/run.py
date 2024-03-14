#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_linkedin_ads import SourceLinkedinAds


def run():
    source = SourceLinkedinAds()
    launch(source, sys.argv[1:])
