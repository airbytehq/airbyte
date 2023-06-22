import sys

from airbyte_cdk.entrypoint import launch
import source

if __name__ == "__main__":
    launch(source.RmsCloudApiKapicheSource(), sys.argv[1:])
