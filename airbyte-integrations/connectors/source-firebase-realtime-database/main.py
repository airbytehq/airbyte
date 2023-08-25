#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_firebase_realtime_database import SourceFirebaseRealtimeDatabase

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceFirebaseRealtimeDatabase()
    launch(source, sys.argv[1:])
