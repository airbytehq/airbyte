#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_nettbutikk24 import SourceNettbutikk24

if __name__ == "__main__":
    source = SourceNettbutikk24()
    launch(source, sys.argv[1:])
