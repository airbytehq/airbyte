#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_dockerhub import SourceDockerhub


def run():
    source = SourceDockerhub()
    launch(source, sys.argv[1:])
