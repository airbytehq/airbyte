#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from base_python.entrypoint import launch
from source_file_secure import SourceFileSecure

if __name__ == "__main__":
    launch(SourceFileSecure(), sys.argv[1:])
