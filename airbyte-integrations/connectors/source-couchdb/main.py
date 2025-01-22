#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import sys

from source_couchdb import SourceCouchdb

from airbyte_cdk.entrypoint import launch


if __name__ == "__main__":
    source = SourceCouchdb()
    launch(source, sys.argv[1:])
