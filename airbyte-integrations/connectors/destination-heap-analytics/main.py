#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from destination_heap_analytics import DestinationHeapAnalytics

if __name__ == "__main__":
    DestinationHeapAnalytics().run(sys.argv[1:])
