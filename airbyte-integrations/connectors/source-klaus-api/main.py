#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_klaus_api import SourceKlausApi

if __name__ == "__main__":
    source = SourceKlausApi()
    launch(source, sys.argv[1:])
