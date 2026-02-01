import sys
from airbyte_cdk import entrypoint
from source_airmeet.source import SourceAirmeet

if __name__ == "__main__":
    source = SourceAirmeet()
    entrypoint.launch(source, sys.argv[1:])