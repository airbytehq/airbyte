#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_commercetools import SourceCommercetools

if __name__ == "__main__":
    source = SourceCommercetools()
    launch(source, sys.argv[1:])
