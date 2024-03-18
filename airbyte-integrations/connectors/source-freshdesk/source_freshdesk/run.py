#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_freshdesk import SourceFreshdesk


def run():
    source = SourceFreshdesk()
    launch(source, sys.argv[1:])
