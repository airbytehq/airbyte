#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_mailersend import SourceMailersend

if __name__ == "__main__":
    source = SourceMailersend()
    launch(source, sys.argv[1:])
