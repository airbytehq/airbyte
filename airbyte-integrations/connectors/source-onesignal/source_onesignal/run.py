#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_onesignal import SourceOnesignal


def run():
    source = SourceOnesignal()
    launch(source, sys.argv[1:])
