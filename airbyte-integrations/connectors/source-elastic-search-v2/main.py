#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_elastic_search_v2 import SourceElasticSearchV2

if __name__ == "__main__":
    source = SourceElasticSearchV2()
    launch(source, sys.argv[1:])
