#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_webflow import SourceWebflow


def run():
    source = SourceWebflow()
    launch(source, sys.argv[1:])
