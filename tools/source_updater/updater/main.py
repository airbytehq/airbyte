import click
import glob
import logging
import os

from airbyte_cdk.connector import BaseConnector
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from updater.catalog import ConfiguredCatalogAssembler, CatalogMerger
from updater.config import Config
from updater.handler import SourceUpdaterHandler
from updater.source import SourceRepository

_DEFAULT_CONFIG_FILE = "config.json"

logger = logging.getLogger("main")


def _assemble_configs(config_path: str):
    """
    :return: the main config and the set of the other configs
    """
    config_files = glob.glob(os.path.join(config_path, "*.json"))
    main_config = None
    other_configs = set()
    for file in config_files:
        if os.path.basename(file) == _DEFAULT_CONFIG_FILE:
            main_config = Config(
                "config",
                dict(
                    BaseConnector.read_config(
                        config_path if config_path.endswith(_DEFAULT_CONFIG_FILE) else os.path.join(config_path, _DEFAULT_CONFIG_FILE)
                    )
                )
            )
        else:
            other_configs.add(
                Config(
                    os.path.basename(file).replace(".json", ""),
                    dict(
                        BaseConnector.read_config(
                            config_path if config_path.endswith(_DEFAULT_CONFIG_FILE) else os.path.join(config_path, _DEFAULT_CONFIG_FILE)
                        )
                    )
                )
            )

    if not main_config:
        raise ValueError(f"Could not find main config. Name should match {_DEFAULT_CONFIG_FILE}")
    return main_config, other_configs


@click.command()
@click.option("--source", type=str, required=True, help="Name of the source. For example, 'source-jira'")
@click.option("--manifest", type=str, required=True, help="Path to the new yaml manifest file")
@click.option("--debug", is_flag=True, default=False, help="Enable debug logs")
def main(source: str, manifest: str, debug: bool) -> None:
    source_name = source
    manifest_path = manifest
    if debug:
        logging.basicConfig(level=logging.DEBUG, force=True)

    logger.info("Starting the update...")
    config_path = f"airbyte-integrations/connectors/{source_name}/secrets/updated_configurations/"
    main_config, other_configs = _assemble_configs(config_path)

    new_manifest_source = YamlDeclarativeSource(manifest_path)
    handler = SourceUpdaterHandler(SourceRepository(), CatalogMerger(ConfiguredCatalogAssembler()))
    handler.handle(source_name, new_manifest_source, main_config, other_configs)

    logger.info(f"Successfully updated source `{source_name}`!")


if __name__ == "__main__":
    main()
