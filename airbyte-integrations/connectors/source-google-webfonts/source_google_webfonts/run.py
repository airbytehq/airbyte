#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_webfonts import SourceGoogleWebfonts


def run():
    source = SourceGoogleWebfonts()
    launch(source, sys.argv[1:])
