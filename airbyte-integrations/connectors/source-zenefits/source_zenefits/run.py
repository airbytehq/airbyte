#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zenefits import SourceZenefits


def run():
    source = SourceZenefits()
    launch(source, sys.argv[1:])
