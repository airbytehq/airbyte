#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_ads import SourceGoogleAds

if __name__ == "__main__":
    source = SourceGoogleAds()
    launch(source, sys.argv[1:])
