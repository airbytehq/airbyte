#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zenefits import SourceZenefits

if __name__ == "__main__":
    source = SourceZenefits()
    launch(source, sys.argv[1:])
