#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os

import click
from typing import Optional, List
from airbyte_cdk.connector_builder.migrator.source import SourceRepository

logger = logging.getLogger("migrator.main")

current_repository = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../../.."))


@click.command()
@click.option("--repository", type=str, required=True, help="Path of the airbytehq/airbyte git repository's root directory", default=current_repository)
@click.option("--source", type=str, required=False, help="Path to a single source to migrate. If this is not provided, all possible sources will be migrated.")
@click.option("--skip", multiple=True, default=[], type=str, help="Directory name of a source to skip. Can be used multiple times.")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose mode.')
def main(repository: str, skip: List[str], source: Optional[str], verbose: bool) -> None:
    if verbose:
        logging.basicConfig(level=logging.DEBUG, force=True)
    else:
        logging.basicConfig(level=logging.INFO, force=True)

    logger.info(f"Starting to migrate connectors in {repository}...")
    repo = SourceRepository(repository)

    if source:
        resolved_source = repo.resolve_no_code_source_path(source)
        if resolved_source:
            logger.debug(f"Trying to migrate {resolved_source}...")
            repo.merge_spec_inside_manifest(resolved_source)
            repo.merge_schemas_inside_manifest(resolved_source)
            repo.delete_schemas_folder(resolved_source)
            logger.debug(f"Successfully updated source `{resolved_source}`!")
        else:
            logger.error(f"{source} is not a no-code source")
            raise click.Abort()
    else:
        for source_name in repo.fetch_no_code_sources(skip_list=skip):
            logger.debug(f"Trying to migrate {source_name}...")
            repo.merge_spec_inside_manifest(source_name)
            repo.merge_schemas_inside_manifest(source_name)
            repo.delete_schemas_folder(source_name)
            logger.debug(f"Successfully updated source `{source_name}`!")
    logger.info("Migration successful!")


if __name__ == "__main__":
    main()
