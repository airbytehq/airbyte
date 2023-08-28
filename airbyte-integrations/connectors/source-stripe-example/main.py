#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_stripe_example import SourceStripeExample

if __name__ == "__main__":
    source = SourceStripeExample()
    launch(source, sys.argv[1:])
