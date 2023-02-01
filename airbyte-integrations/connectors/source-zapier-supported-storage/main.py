#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zapier_supported_storage import SourceZapierSupportedStorage

if __name__ == "__main__":
    source = SourceZapierSupportedStorage()
    launch(source, sys.argv[1:])
