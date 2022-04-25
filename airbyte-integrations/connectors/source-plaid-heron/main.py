#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_plaid_heron import SourcePlaidHeron

if __name__ == "__main__":
    source = SourcePlaidHeron()
    launch(source, sys.argv[1:])
