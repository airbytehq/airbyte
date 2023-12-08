#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_visma_economic import SourceVismaEconomic

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceVismaEconomic()
    launch(source, sys.argv[1:])
