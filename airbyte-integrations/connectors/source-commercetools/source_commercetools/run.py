#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_commercetools import SourceCommercetools

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch


def run():
    args = sys.argv[1:]
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    config_path = AirbyteEntrypoint.extract_config(args)
    state_path = AirbyteEntrypoint.extract_state(args)
    source = SourceCommercetools(
        SourceCommercetools.read_catalog(catalog_path) if catalog_path else None,
        SourceCommercetools.read_config(config_path) if config_path else None,
        SourceCommercetools.read_state(state_path) if state_path else None,
    )
    launch(source, args)
