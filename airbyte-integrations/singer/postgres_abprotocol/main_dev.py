import sys
from airbyte_protocol.entrypoint import launch

from postgres_singer_source import PostgresSingerSource

if __name__ == "__main__":
    source = PostgresSingerSource()
    launch(source, sys.argv[1:])
