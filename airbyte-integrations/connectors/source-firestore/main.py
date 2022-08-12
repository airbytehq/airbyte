#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_firestore import SourceFirestore

if __name__ == "__main__":
    source = SourceFirestore()
    launch(source, sys.argv[1:])
