#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_facebook_pages import SourceFacebookPages


def run():
    source = SourceFacebookPages()
    launch(source, sys.argv[1:])
