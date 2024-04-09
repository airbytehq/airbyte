#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_apple_app_store_connect import SourceAppleAppStoreConnect

if __name__ == "__main__":
    source = SourceAppleAppStoreConnect()
    launch(source, sys.argv[1:])
