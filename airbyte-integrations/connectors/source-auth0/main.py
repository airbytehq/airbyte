#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_auth0 import SourceAuth0

if __name__ == "__main__":
    source = SourceAuth0()
    launch(source, sys.argv[1:])
