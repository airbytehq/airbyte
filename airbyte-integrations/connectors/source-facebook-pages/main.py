#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_facebook_pages import SourceFacebookPages

if __name__ == "__main__":
    source = SourceFacebookPages()
    launch(source, sys.argv[1:])
