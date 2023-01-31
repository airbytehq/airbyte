#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_smi2_mirtesen import SourceSmi2Mirtesen

if __name__ == "__main__":
    source = SourceSmi2Mirtesen()
    launch(source, sys.argv[1:])
