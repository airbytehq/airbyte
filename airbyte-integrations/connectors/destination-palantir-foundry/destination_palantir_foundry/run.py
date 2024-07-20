#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import sys

from .destination import DestinationPalantirFoundry


def run():
    destination = DestinationPalantirFoundry()
    destination.run(sys.argv[1:])
