#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_stripe import SourceStripe

if __name__ == "__main__":
    source = SourceStripe()
    launch(source, sys.argv[1:])
