#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_mailgun import SourceMailgun


def run():
    source = SourceMailgun()
    launch(source, sys.argv[1:])
