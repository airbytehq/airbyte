import sys
from airbyte_cdk.entrypoint import launch
from source_airmeet import SourceAirmeet

if __name__ == "__main__":
    source = SourceAirmeet()
    launch(source, sys.argv[1:])