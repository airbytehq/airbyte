#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_nasa_apod import SourceNasaApod

if __name__ == "__main__":
    source = SourceNasaApod()
    launch(source, sys.argv[1:])
