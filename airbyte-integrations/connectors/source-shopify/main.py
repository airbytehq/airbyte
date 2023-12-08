#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_shopify import SourceShopify

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceShopify()
    launch(source, sys.argv[1:])
