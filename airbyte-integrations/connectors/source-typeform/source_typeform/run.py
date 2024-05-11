#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_typeform import SourceTypeform


def run():
    source = SourceTypeform()
    launch(source, sys.argv[1:])
