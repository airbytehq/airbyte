import sys

from airbyte_cdk.entrypoint import launch

from .source import SourceGoogleAdManager


def run():
    source = SourceGoogleAdManager()
    launch(source, sys.argv[1:])
