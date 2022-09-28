#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_find_supabase import SourceFindSupabase

if __name__ == "__main__":
    source = SourceFindSupabase()
    launch(source, sys.argv[1:])
