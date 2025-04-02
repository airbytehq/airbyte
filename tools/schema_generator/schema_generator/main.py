#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import argparse
import sys

from .configure_catalog import configure_catalog
from .infer_schemas import infer_schemas


def main():
    parser = argparse.ArgumentParser(description="Airbyte Schema Generator")

    if len(sys.argv) == 1:
        parser.print_help()

    parser.add_argument("--configure-catalog", action="store_true", help="Generate a Configured Catalog")
    parser.add_argument("--infer-schemas", action="store_true", help="Infer Stream Schemas")

    args, unknown_args = parser.parse_known_args()

    if unknown_args:
        print(f"Invalid arguments: {unknown_args}.")
        parser.print_help()
    elif args.configure_catalog:
        configure_catalog()
    elif args.infer_schemas:
        infer_schemas()


if __name__ == "__main__":
    sys.exit(main())
