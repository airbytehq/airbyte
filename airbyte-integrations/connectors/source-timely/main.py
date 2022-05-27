#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_timely_integration import SourceTimelyIntegration

if __name__ == "__main__":
    source = SourceTimelyIntegration()
    launch(source, sys.argv[1:])
