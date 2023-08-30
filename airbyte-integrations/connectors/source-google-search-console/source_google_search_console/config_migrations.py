#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import sys
from typing import Any, List, Mapping

from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources import Source

logger = logging.getLogger("airbyte_logger")


class MigrateCustomReports:
    """
    This class stands for migrating the config at runtime,
    while providing the backward compatibility when falling back to the previous source version.

    Specifically, starting from `1.3.3`, the `custom_reports` property should be like :
        >   List([{name: my_report}, {dimensions: [a,b,c]}], [], ...)
    instead of, in `1.3.2`:
        >   JSON STR: "{name: my_report}, {dimensions: [a,b,c]}"
    """

    depercated_message: str = """
        The `Custom Reports` declared using the deprecated structure of JSON String and are transfomed automatically.
        Please update the `Custom Reports` structue for this source.
        Visit: `Sources > select your `Google Search Console` source > Settings > Custom Reports` and update the section using built-in report builder."
    """

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """
        This method determines wether or not the config should be migrated to have the new structure for the `custom_reports`
        Returns:
            > True, if the transformation is neccessary
        Or
            > False, otherwise.
        Or
            > Raises the Exception if the structure could not be migrated.
        """

        if "custom_reports" in config:
            custom_reports = config["custom_reports"]
            # check the old structure first
            if isinstance(custom_reports, str):
                logger.warning(cls.depercated_message)
                return True
            # if the structure is new - bypass the transformation
            elif isinstance(custom_reports, list):
                return False
            # raise an error otherwise
            else:
                raise Exception(
                    f"Custom Reports have invalid structure of {type(custom_reports)}, the structure should be either JSON String or List of Objects."
                )
        return False

    @classmethod
    def transform(cls, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        # transfom `json_str` to `list` of objects
        return source._validate_custom_reports(config)

    @classmethod
    def migrate(cls, source: Source) -> List[str]:
        """
        This method checks the input args, should the config be migrated or not, transform if neccessary.

        Returns:
            > The list of updated input args, if the transformation was applied to the config
        Or
            > The list of original input args, otherwise.
        """
        # get input args
        args = sys.argv[1:]
        # get config path
        config_path = AirbyteEntrypoint(source).extract_config(args)
        # proceed only if `--config` arg is provided
        if config_path:
            # read the existing config
            config = source.read_config(config_path)
            # migration check
            if cls.should_migrate(config):
                # make new path for migrated config
                migated_config_path = config_path.replace("config", "migrated_config")
                # modify the config
                migrated_config = cls.transform(source, config)
                # save the config
                source.write_config(migrated_config, migated_config_path)
                # update the config path after the migration

                # return updated args
                return cls.replace_config_path(args, config_path, migated_config_path)
            # return old config path otherwise
        return args

    @classmethod
    def replace_config_path(cls, args: List[str], config_path: str, migrated_config_path: str) -> List[str]:
        """
        This method replaces the `config_path` reference inside the original input args,
        to provide the migrated_config_path, if the transformation was applied, leaving the exising config intact.

        The advanteges of such approach is the backward compatibility with the older version of the source,
        because the migrated_config stored at runtime of the source connector,
        and re-creates every time the `check/discover/read` triggers.
        """
        return list(map(lambda x: x.replace(config_path, migrated_config_path), args))
