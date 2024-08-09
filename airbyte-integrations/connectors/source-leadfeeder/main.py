#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_leadfeeder import SourceLeadfeeder

if __name__ == "__main__":
    source = SourceLeadfeeder()
    launch(source, sys.argv[1:])
