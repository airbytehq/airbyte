import sys

from airbyte_cdk.entrypoint import launch
from source_bold import SourceBold

if __name__ == "__main__":
    source = SourceBold()
    launch(source, sys.argv[1:])
