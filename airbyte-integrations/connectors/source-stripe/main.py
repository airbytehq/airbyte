#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from source_stripe import SourceStripe

if __name__ == "__main__":
    args = sys.argv[1:]
    catalog = AirbyteEntrypoint.extract_catalog(args)
    source = SourceStripe(catalog)
    launch(source, args)
