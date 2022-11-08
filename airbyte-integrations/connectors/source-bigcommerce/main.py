#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_bigcommerce import SourceBigcommerce

if __name__ == "__main__":
    source = SourceBigcommerce()
    launch(source, sys.argv[1:])
