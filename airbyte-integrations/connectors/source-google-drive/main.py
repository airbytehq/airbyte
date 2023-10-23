#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_drive import SourceGoogleDrive

if __name__ == "__main__":
    source = SourceGoogleDrive()
    launch(source, sys.argv[1:])
