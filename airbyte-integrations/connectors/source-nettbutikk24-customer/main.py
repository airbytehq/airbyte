#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_nettbutikk24_customer import SourceNettbutikk24Customer

if __name__ == "__main__":
    source = SourceNettbutikk24Customer()
    launch(source, sys.argv[1:])
