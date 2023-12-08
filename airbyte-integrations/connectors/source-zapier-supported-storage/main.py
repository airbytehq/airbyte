#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_zapier_supported_storage import SourceZapierSupportedStorage

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceZapierSupportedStorage()
    launch(source, sys.argv[1:])
