#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_prestashop import SourcePrestashop

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourcePrestashop()
    launch(source, sys.argv[1:])
