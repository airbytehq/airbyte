#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_klaviyo import SourceKlaviyo


def run():
    source = SourceKlaviyo()
    launch(source, sys.argv[1:])
