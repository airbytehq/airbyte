#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_surveycto import SourceSurveycto


def run():
    source = SourceSurveycto()
    launch(source, sys.argv[1:])
