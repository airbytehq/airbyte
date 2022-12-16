#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_tripletex_api import SourceTripletexApi

if __name__ == "__main__":
    source = SourceTripletexApi()
    launch(source, sys.argv[1:])
