#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk import AirbyteEntrypoint
from airbyte_cdk.entrypoint import launch
from source_microsoft_sharepoint import SourceMicrosoftSharePoint

if __name__ == "__main__":
    args = sys.argv[1:]
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    source = SourceMicrosoftSharePoint(catalog_path)
    launch(source, args)
