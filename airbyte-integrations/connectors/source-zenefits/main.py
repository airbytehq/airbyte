#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_zenefits import SourceZenefits

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceZenefits()
    launch(source, sys.argv[1:])
