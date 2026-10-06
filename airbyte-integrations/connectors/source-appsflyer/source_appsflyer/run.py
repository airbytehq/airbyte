#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_appsflyer import SourceAppsflyer


def run():
    source = SourceAppsflyer()
    launch(source, sys.argv[1:])
