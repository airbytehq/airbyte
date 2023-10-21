#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import sys

# logging.basicConfig(level='DEBUG')
from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from source_stripe import SourceStripe

if __name__ == "__main__":
    import faulthandler

    # logging.basicConfig(level='DEBUG')

    faulthandler.enable()
    args = sys.argv[1:]
    state = AirbyteEntrypoint.extract_state(args)
    use_concurrent_cdk = state is None
    source = SourceStripe(use_concurrent_cdk=True)
    launch(source, args)
