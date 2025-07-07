#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_nexus_datasets import SourceNexusDatasets

if __name__ == "__main__":
    source = SourceNexusDatasets()
    launch(source, sys.argv[1:])
