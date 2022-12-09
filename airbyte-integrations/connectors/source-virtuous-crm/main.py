#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_virtuous_crm import SourceVirtuousCrm

if __name__ == "__main__":
    source = SourceVirtuousCrm()
    launch(source, sys.argv[1:])
