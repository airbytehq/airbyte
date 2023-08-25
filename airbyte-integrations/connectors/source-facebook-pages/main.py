#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_facebook_pages import SourceFacebookPages

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceFacebookPages()
    launch(source, sys.argv[1:])
