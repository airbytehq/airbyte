#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from source_zenhub_graphql.run import run
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
