#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_google_webfonts import SourceGoogleWebfonts

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceGoogleWebfonts()
    launch(source, sys.argv[1:])
