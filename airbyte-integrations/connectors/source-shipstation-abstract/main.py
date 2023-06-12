#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_shipstation_abstract import SourceShipstationAbstract

if __name__ == "__main__":
    source = SourceShipstationAbstract()
    launch(source, sys.argv[1:])
