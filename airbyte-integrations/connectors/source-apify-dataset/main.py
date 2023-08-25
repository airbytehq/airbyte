#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_apify_dataset import SourceApifyDataset

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceApifyDataset()
    launch(source, sys.argv[1:])
