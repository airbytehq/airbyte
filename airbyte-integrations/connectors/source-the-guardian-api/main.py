#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_the_guardian_api import SourceTheGuardianApi

if __name__ == "__main__":
    source = SourceTheGuardianApi()
    launch(source, sys.argv[1:])
