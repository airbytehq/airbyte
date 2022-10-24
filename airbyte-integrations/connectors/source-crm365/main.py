#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_crm_365 import SourceCrm365

if __name__ == "__main__":
    source = SourceCrm365()
    launch(source, sys.argv[1:])
