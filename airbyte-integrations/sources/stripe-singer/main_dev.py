import sys
from airbyte_protocol.entrypoint import launch

from source_stripe_singer import SourceStripeSinger

if __name__ == "__main__":
    source = SourceStripeSinger()
    launch(source, sys.argv[1:])
