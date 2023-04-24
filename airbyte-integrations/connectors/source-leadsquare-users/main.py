#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_leadsquare_users import SourceLeadsquareUsers

if __name__ == "__main__":
    source = SourceLeadsquareUsers()
    launch(source, sys.argv[1:])
