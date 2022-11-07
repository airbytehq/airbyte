#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_public_apis import SourcePublicApis

if __name__ == "__main__":
    source = SourcePublicApis()
    launch(source, sys.argv[1:])
