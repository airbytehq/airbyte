#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from destination_planhat_analytics import DestinationPlanhatAnalytics

if __name__ == "__main__":
    DestinationPlanhatAnalytics().run(sys.argv[1:])
