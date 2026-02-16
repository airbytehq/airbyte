import sys

from airbyte_cdk.entrypoint import launch
from source_tulip.source import SourceTulip


if __name__ == "__main__":
    source = SourceTulip()
    launch(source, sys.argv[1:])
