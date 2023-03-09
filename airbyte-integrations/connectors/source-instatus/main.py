#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_instatus import SourceInstatus

if __name__ == "__main__":
    source = SourceInstatus()
    launch(source, sys.argv[1:])
