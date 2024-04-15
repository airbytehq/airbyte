#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_dealfront import SourceDealfront

if __name__ == "__main__":
    source = SourceDealfront()
    launch(source, sys.argv[1:])
