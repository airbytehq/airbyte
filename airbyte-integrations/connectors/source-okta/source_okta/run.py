#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_okta import SourceOkta


def run():
    source = SourceOkta()
    launch(source, sys.argv[1:])
