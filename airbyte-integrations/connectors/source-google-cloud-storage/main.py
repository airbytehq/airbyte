#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_cloud_storage import SourceGoogleCloudStorage

if __name__ == "__main__":
    source = SourceGoogleCloudStorage()
    launch(source, sys.argv[1:])
