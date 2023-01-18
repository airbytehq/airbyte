#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_visma_economic import SourceVismaEconomic

if __name__ == "__main__":
    source = SourceVismaEconomic()
    launch(source, sys.argv[1:])
