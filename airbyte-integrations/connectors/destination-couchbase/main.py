#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from destination_couchbase import DestinationCouchbase


if __name__ == "__main__":
    DestinationCouchbase().run(sys.argv[1:])
