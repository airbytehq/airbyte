import sys
from airbyte_protocol.entrypoint import launch

from source_exchangeratesapi_singer import SourceExchangeRatesApiSinger

if __name__ == "__main__":
    source = SourceExchangeRatesApiSinger()
    launch(source, sys.argv[1:])
