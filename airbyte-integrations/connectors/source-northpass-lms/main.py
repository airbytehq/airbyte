#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_northpass_lms import SourceNorthpassLms

if __name__ == "__main__":
    source = SourceNorthpassLms()
    launch(source, sys.argv[1:])
