#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_google_ads import SourceGoogleAds

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceGoogleAds()
    launch(source, sys.argv[1:])
