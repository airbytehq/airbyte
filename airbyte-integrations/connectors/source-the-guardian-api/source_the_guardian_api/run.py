#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_the_guardian_api import SourceTheGuardianApi


def run():
    source = SourceTheGuardianApi()
    launch(source, sys.argv[1:])
