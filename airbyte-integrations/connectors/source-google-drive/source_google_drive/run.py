#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk import AirbyteEntrypoint
from airbyte_cdk.entrypoint import launch
from source_google_drive import SourceGoogleDrive


def run():
    args = sys.argv[1:]
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    config_path = AirbyteEntrypoint.extract_config(args)
    state_path = AirbyteEntrypoint.extract_state(args)
    source = SourceGoogleDrive(
        SourceGoogleDrive.read_catalog(catalog_path) if catalog_path else None,
        SourceGoogleDrive.read_config(config_path) if config_path else None,
        SourceGoogleDrive.read_state(state_path) if state_path else None,
    )
    launch(source, args)
