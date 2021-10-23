#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_opentable_sync_api import SourceOpentableSyncApi

if __name__ == "__main__":
    source = SourceOpentableSyncApi()
    launch(source, sys.argv[1:])
