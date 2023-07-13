import glob
import logging
import os

from airbyte_cdk.connector import BaseConnector
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from updater.catalog import CatalogAssembler, CatalogMerger
from updater.config import Config
from updater.handler import SourceUpdaterHandler
from updater.source import SourceRepository

_DEFAULT_CONFIG_FILE = "config.json"

logger = logging.getLogger("main")


def _assemble_configs(config_path: str):
    """
    :return: the main config and the set of the other configs
    """
    if os.path.isfile(config_path):
        return Config(
            "config",
            BaseConnector.read_config(
                config_path if config_path.endswith(_DEFAULT_CONFIG_FILE) else os.path.join(config_path, _DEFAULT_CONFIG_FILE)
            )
        ), set()

    config_files = glob.glob(os.path.join(config_path, "*.json"))
    main_config = None
    other_configs = set()
    for file in config_files:
        if os.path.basename(file) == _DEFAULT_CONFIG_FILE:
            main_config = Config(
                "config",
                BaseConnector.read_config(
                    config_path if config_path.endswith(_DEFAULT_CONFIG_FILE) else os.path.join(config_path, _DEFAULT_CONFIG_FILE)
                )
            )
        else:
            other_configs.add(
                Config(
                    os.path.basename(file).replace(".json", ""),
                    BaseConnector.read_config(
                        config_path if config_path.endswith(_DEFAULT_CONFIG_FILE) else os.path.join(config_path, _DEFAULT_CONFIG_FILE)
                    )
                )
            )

    if not main_config:
        raise ValueError(f"Could not find main config. Name should match {_DEFAULT_CONFIG_FILE}")
    return main_config, other_configs


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Source updated",
    )
    parser.add_argument("--source", type=str, required=True, help="Name of the source. For example, 'source-jira'")
    parser.add_argument("--manifest", type=str, required=True, help="Path to the new yaml manifest file")
    parser.add_argument("--config", type=str, required=True, help="Path to the config file or directory. We recommend using `airbyte-integrations/connectors/<source_name>/secrets/updated_configurations/*.json`")
    parser.add_argument("--debug", default=False, required=False, action='store_true', help="Enable debug logs")

    args = parser.parse_args()
    source_name = args.source
    manifest_path = args.manifest
    config_path = args.config
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, force=True)

    logger.info("Starting the update...")
    repo = SourceRepository()
    main_config, other_configs = _assemble_configs(config_path)

    new_manifest_source = YamlDeclarativeSource(manifest_path)
    handler = SourceUpdaterHandler(repo, CatalogMerger(repo, CatalogAssembler()))
    handler.handle(source_name, new_manifest_source, main_config, other_configs)

    logger.info(f"Successfully updated source `{source_name}`!")
