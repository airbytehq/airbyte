#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_plaid import SourcePlaid

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourcePlaid()
    launch(source, sys.argv[1:])
