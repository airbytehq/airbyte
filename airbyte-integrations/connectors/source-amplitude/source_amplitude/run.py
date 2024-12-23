#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_amplitude import SourceAmplitude

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceAmplitude()
    launch(source, sys.argv[1:])
