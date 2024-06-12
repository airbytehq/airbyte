#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_everhour import SourceEverhour


def run():
    source = SourceEverhour()
    launch(source, sys.argv[1:])
