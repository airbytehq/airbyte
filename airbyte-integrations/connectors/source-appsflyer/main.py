#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_appsflyer import SourceAppsflyer

if __name__ == "__main__":
    source = SourceAppsflyer()
    launch(source, sys.argv[1:])
