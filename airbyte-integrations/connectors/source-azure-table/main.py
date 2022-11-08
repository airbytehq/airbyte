#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_azure_table import SourceAzureTable

if __name__ == "__main__":
    source = SourceAzureTable()
    launch(source, sys.argv[1:])
