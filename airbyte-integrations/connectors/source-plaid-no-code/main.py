#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_plaid_no_code import SourcePlaidNoCode

if __name__ == "__main__":
    source = SourcePlaidNoCode()
    launch(source, sys.argv[1:])
