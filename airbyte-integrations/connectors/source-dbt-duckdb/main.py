#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
"""
This file exists to allow running the connector with `python main.py`, which is a
convention expected by the airbyte connector builder.
"""


from source_dbt_duckdb import cli


def main():
    cli.main()


if __name__ == "__main__":
    main()
