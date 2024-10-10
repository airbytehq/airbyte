#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from destination_lime_crm import DestinationLimeCrm

if __name__ == "__main__":
    DestinationLimeCrm().run(sys.argv[1:])
