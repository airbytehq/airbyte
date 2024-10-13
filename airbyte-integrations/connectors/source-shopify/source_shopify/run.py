#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
from typing import List

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
#from source_shopify.config_migrations import MigrateConfig
from .source import LTKSourceShopify

from .source import SourceShopify, LTKSourceShopify
from .config import DatabaseClient, AWSClient

def _get_source(args: List[str]):
    config_path = AirbyteEntrypoint.extract_config(args)
    config = SourceShopify.read_config(config_path) if config_path else None
    db_client = DatabaseClient(config) if config else None
    aws_client = AWSClient(config) if config else None
    return LTKSourceShopify(db_client, aws_client)

def run() -> None:
    
    _args = sys.argv[1:]
    source = _get_source(_args)
    # migrate config at runtime
    #MigrateConfig.migrate(sys.argv[1:], source)

    # run the connector
    launch(source, sys.argv[1:])
