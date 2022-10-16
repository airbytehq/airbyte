#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_apify_dataset import SourceApifyDataset

if __name__ == "__main__":
    source = SourceApifyDataset()
    launch(source, sys.argv[1:])
