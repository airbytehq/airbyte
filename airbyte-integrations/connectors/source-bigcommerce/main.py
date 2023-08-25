#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_bigcommerce import SourceBigcommerce

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceBigcommerce()
    launch(source, sys.argv[1:])
