#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_appstore_singer import SourceAppstoreSinger


def run():
    source = SourceAppstoreSinger()
    launch(source, sys.argv[1:])
