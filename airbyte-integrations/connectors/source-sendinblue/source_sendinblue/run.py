#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_sendinblue import SourceSendinblue


def run():
    source = SourceSendinblue()
    launch(source, sys.argv[1:])
