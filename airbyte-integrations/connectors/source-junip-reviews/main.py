#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_junip_reviews import SourceJunipReviews

if __name__ == "__main__":
    source = SourceJunipReviews()
    launch(source, sys.argv[1:])
