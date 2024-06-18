#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from destination_glide import DestinationGlide

if __name__ == "__main__":
    DestinationGlide().run(sys.argv[1:])
