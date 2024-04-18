#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_shopify.config_migrations import MigrateConfig

from .source import SourceShopify


def run() -> None:
    source = SourceShopify()
    # migrate config at runtime
    MigrateConfig.migrate(sys.argv[1:], source)
    # run the connector
    launch(source, sys.argv[1:])
