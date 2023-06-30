import sys

from airbyte_cdk.entrypoint import launch
from source.source import RmsCloudApiKapicheSource

if __name__ == "__main__":
    launch(RmsCloudApiKapicheSource(), sys.argv[1:])
