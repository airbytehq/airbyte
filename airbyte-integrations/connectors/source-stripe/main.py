#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from source_stripe import SourceStripe


if __name__ == "__main__":
    args = sys.argv[1:]
    state = SourceStripe.read_state(AirbyteEntrypoint.extract_state(args))
    catalog = SourceStripe.read_catalog(AirbyteEntrypoint.extract_catalog(args))
    source = SourceStripe(state, catalog, use_concurrent_cdk=True)
    launch(source, args)
