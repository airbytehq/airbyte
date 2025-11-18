#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import sys

from source_nexus_datasets import SourceNexusDatasets

from airbyte_cdk.entrypoint import launch


if __name__ == "__main__":
    source = SourceNexusDatasets()
    launch(source, sys.argv[1:])
