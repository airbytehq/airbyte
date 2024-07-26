#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from destination_palantir_foundry import DestinationPalantirFoundry

if __name__ == "__main__":
    DestinationPalantirFoundry().run(sys.argv[1:])
