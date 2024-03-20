#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_datacraft_static_table import SourceDatacraftStaticTable

if __name__ == "__main__":
    source = SourceDatacraftStaticTable()
    launch(source, sys.argv[1:])
