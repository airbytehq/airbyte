#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_instagram import SourceInstagram


def run():
    source = SourceInstagram()
    launch(source, sys.argv[1:])
