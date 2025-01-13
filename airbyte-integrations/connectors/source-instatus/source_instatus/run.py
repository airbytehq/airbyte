#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_instatus import SourceInstatus

from airbyte_cdk.entrypoint import launch


def run():
    source = SourceInstatus()
    launch(source, sys.argv[1:])
