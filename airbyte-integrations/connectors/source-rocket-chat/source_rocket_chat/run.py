#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_rocket_chat import SourceRocketChat


def run():
    source = SourceRocketChat()
    launch(source, sys.argv[1:])
