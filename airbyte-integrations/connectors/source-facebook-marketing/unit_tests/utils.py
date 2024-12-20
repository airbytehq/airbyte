#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest import mock

from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit, split_config


def command_check(source: Source, config):
    logger = mock.MagicMock()
    connector_config, _ = split_config(config)
    if source.check_config_against_spec:
        source_spec: ConnectorSpecification = source.spec(logger)
        check_config_against_spec_or_exit(connector_config, source_spec)
    return source.check(logger, config)
