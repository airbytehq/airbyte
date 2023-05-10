#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_telegram import SourceTelegram

if __name__ == "__main__":
    source = SourceTelegram()
    launch(source, sys.argv[1:])
