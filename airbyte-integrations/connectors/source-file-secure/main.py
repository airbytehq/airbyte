#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_file_secure import SourceFileSecure

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    launch(SourceFileSecure(), sys.argv[1:])
