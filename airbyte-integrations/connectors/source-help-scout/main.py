#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_help_scout import SourceHelpScout

if __name__ == "__main__":
    source = SourceHelpScout()
    launch(source, sys.argv[1:])
