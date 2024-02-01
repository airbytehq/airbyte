#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_amazon_ads import SourceAmazonAds
from source_amazon_ads.config_migrations import MigrateStartDate


def run():
    source = SourceAmazonAds()
    MigrateStartDate.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
