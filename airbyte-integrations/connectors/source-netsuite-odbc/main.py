#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_netsuite_odbc import SourceNetsuiteOdbc

if __name__ == "__main__":
    source = SourceNetsuiteOdbc()
    launch(source, sys.argv[1:])
