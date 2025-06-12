#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_facebook_pages import SourceFacebookPages

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceFacebookPages()
    launch(source, sys.argv[1:])
