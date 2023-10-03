#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_odnoklassniki_groups import SourceOdnoklassnikiGroups

if __name__ == "__main__":
    source = SourceOdnoklassnikiGroups()
    launch(source, sys.argv[1:])
