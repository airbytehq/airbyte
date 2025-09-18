import sys
from airbyte_cdk.entrypoint import launch
from .destination import DestinationMockapi

def run():
    destination = DestinationMockapi()
    launch(destination, sys.argv[1:])