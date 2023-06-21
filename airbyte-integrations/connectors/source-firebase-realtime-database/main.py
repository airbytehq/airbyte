#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_firebase_realtime_database import SourceFirebaseRealtimeDatabase

if __name__ == "__main__":
    source = SourceFirebaseRealtimeDatabase()
    launch(source, sys.argv[1:])
