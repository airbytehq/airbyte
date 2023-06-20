import sys

from airbyte_cdk.entrypoint import launch
import source

if __name__ == "__main__":
    launch(source.Source(), sys.argv[1:])
