#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_google_pagespeed_insights import SourceGooglePagespeedInsights

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceGooglePagespeedInsights()
    launch(source, sys.argv[1:])
