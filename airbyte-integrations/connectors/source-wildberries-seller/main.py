#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_wildberries_seller import SourceWildberriesSeller

if __name__ == "__main__":
    source = SourceWildberriesSeller()
    launch(source, sys.argv[1:])
