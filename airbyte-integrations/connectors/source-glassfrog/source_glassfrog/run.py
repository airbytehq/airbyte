#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_glassfrog import SourceGlassfrog


def run():
    source = SourceGlassfrog()
    launch(source, sys.argv[1:])
