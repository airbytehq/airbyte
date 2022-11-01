#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_courier import SourceCourier

if __name__ == "__main__":
    source = SourceCourier()
    launch(source, sys.argv[1:])
