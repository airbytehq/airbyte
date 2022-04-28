#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_shipstation import SourceShipstation

if __name__ == "__main__":
    source = SourceShipstation()
    launch(source, sys.argv[1:])
