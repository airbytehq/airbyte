#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_linkedin_ads import SourceLinkedinAds
from source_linkedin_ads.config_migrations import MigrateCredentials


def run():
    source = SourceLinkedinAds()
    MigrateCredentials.migrate(sys.argv[1:], source)
    launch(source, sys.argv[1:])
