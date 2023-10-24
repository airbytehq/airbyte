#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from source_stripe import SourceStripe

if __name__ == "__main__":
    args = sys.argv[1:]
    # Use the presence of a state file as a proxy for whether we're running in full refresh
    state = AirbyteEntrypoint.extract_state(args)
    use_concurrent_cdk = state is None
    source = SourceStripe(use_concurrent_cdk=use_concurrent_cdk)
    launch(source, args)
