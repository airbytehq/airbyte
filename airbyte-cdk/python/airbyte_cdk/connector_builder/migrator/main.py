#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import click
from airbyte_cdk.connector_builder.migrator.source import SourceRepository

logger = logging.getLogger("migrator.main")


@click.command()
@click.option("--repository", type=str, required=True, help="Path of the airbytehq/airbyte")
def main(repository: str) -> None:
    logging.basicConfig(level=logging.DEBUG, force=True)

    logger.info("Starting the migration...")
    repo = SourceRepository(repository)
    for source_name in repo.fetch_no_code_sources():
        logger.debug(f"Trying to migrate {source_name}...")
        repo.merge_spec_inside_manifest(source_name)
        logger.debug(f"Successfully updated source `{source_name}`!")
    logger.info("Migration successful!")


if __name__ == "__main__":
    main()
