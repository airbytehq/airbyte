#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_crowdstrike_falcon import SourceCrowdstrikeFalcon

if __name__ == "__main__":
    source = SourceCrowdstrikeFalcon()
    launch(source, sys.argv[1:])
