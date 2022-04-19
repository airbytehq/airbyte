#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from destination_firestore import DestinationFirestore

if __name__ == "__main__":
    DestinationFirestore().run(sys.argv[1:])
