#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_prestashop import SourcePrestaShop

if __name__ == "__main__":
    source = SourcePrestaShop()
    launch(source, sys.argv[1:])
