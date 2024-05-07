#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_amazon_ads import SourceAmazonAds
from source_amazon_ads.config_migrations import MigrateStartDate
from source_amazon_ads.declarative_source_adapter import DeclarativeSourceAdapter


def run():
    source = DeclarativeSourceAdapter(source=SourceAmazonAds())
    MigrateStartDate.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
