#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_public_apis import SourcePublicApis

from airbyte_cdk.entrypoint import launch


def run():
    source = SourcePublicApis()
    launch(source, sys.argv[1:])
