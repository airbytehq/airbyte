#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_pagespeed_insights import SourceGooglePagespeedInsights

if __name__ == "__main__":
    source = SourceGooglePagespeedInsights()
    launch(source, sys.argv[1:])
