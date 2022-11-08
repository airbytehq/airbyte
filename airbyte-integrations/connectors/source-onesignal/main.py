#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_onesignal import SourceOnesignal

if __name__ == "__main__":
    source = SourceOnesignal()
    launch(source, sys.argv[1:])
