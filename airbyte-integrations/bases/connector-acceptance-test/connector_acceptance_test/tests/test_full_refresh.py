#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import time
from collections import defaultdict
from functools import partial
from logging import Logger
from typing import List, Mapping, Optional

import pytest
from airbyte_protocol.models import ConfiguredAirbyteCatalog, Type
from connector_acceptance_test.base import BaseTest
from connector_acceptance_test.config import IgnoredFieldsConfiguration
from connector_acceptance_test.utils import ConnectorRunner, JsonSchemaHelper, SecretDict, full_refresh_only_catalog, make_hashable
from connector_acceptance_test.utils.json_schema_helper import CatalogField
from connector_acceptance_test.utils.timeouts import TWENTY_MINUTES


def primary_keys_by_stream(configured_catalog: ConfiguredAirbyteCatalog) -> Mapping[str, List[CatalogField]]:
    """Get PK fields for each stream

    :param configured_catalog:
    :return:
    """
    data = {}
    for stream in configured_catalog.streams:
        helper = JsonSchemaHelper(schema=stream.stream.json_schema)
        pks = stream.primary_key or []
        data[stream.stream.name] = [helper.field(pk) for pk in pks]

    return data


def primary_keys_only(record, pks):
    return ";".join([f"{pk.path}={pk.parse(record)}" for pk in pks])


@pytest.mark.default_timeout(TWENTY_MINUTES)
class TestFullRefresh(BaseTest):
    def assert_emitted_at_increase_on_subsequent_runs(self, first_read_records, second_read_records):
        first_read_records_data = [record.data for record in first_read_records]
        assert first_read_records_data, "At least one record should be read using provided catalog"

        first_read_records_emitted_at = [record.emitted_at for record in first_read_records]
        max_emitted_at_first_read = max(first_read_records_emitted_at)

        second_read_records_emitted_at = [record.emitted_at for record in second_read_records]

        min_emitted_at_second_read = min(second_read_records_emitted_at)

        assert max_emitted_at_first_read < min_emitted_at_second_read, "emitted_at should increase on subsequent runs"

    async def test_sequential_reads(
        self,
        connector_config: SecretDict,
        configured_catalog: ConfiguredAirbyteCatalog,
        ignored_fields: Optional[Mapping[str, List[IgnoredFieldsConfiguration]]],
        docker_runner: ConnectorRunner,
        detailed_logger: Logger,
    ):
        configured_catalog = full_refresh_only_catalog(configured_catalog)
        output_1 = await docker_runner.call_read(
            connector_config,
            configured_catalog,
            enable_caching=False,
        )
        records_1 = [message.record for message in output_1 if message.type == Type.RECORD]

        # sleep to ensure that the emitted_at timestamp is different
        time.sleep(0.1)

        output_2 = await docker_runner.call_read(connector_config, configured_catalog, enable_caching=False)
        records_2 = [message.record for message in output_2 if message.type == Type.RECORD]

        self.assert_emitted_at_increase_on_subsequent_runs(records_1, records_2)
