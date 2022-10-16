#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_file_secure import SourceFileSecure

if __name__ == "__main__":
    launch(SourceFileSecure(), sys.argv[1:])
