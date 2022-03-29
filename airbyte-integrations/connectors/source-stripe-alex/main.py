#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_stripe_alex import SourceStripeAlex

if __name__ == "__main__":
    source = SourceStripeAlex()
    launch(source, sys.argv[1:])
