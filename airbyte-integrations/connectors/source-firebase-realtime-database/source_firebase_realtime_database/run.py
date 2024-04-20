#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_firebase_realtime_database import SourceFirebaseRealtimeDatabase


def run():
    source = SourceFirebaseRealtimeDatabase()
    launch(source, sys.argv[1:])
