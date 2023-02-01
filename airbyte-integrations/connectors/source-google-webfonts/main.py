#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_webfonts import SourceGoogleWebfonts

if __name__ == "__main__":
    source = SourceGoogleWebfonts()
    launch(source, sys.argv[1:])
