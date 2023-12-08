#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_the_guardian_api import SourceTheGuardianApi

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceTheGuardianApi()
    launch(source, sys.argv[1:])
