#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import time
from collections import defaultdict
from functools import partial
from logging import Logger
from typing import List, Mapping, Optional

import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog, Type
from connector_acceptance_test.base import BaseTest
from connector_acceptance_test.config import IgnoredFieldsConfiguration
from connector_acceptance_test.utils import ConnectorRunner, JsonSchemaHelper, SecretDict, full_refresh_only_catalog, make_hashable
from connector_acceptance_test.utils.json_schema_helper import CatalogField


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


@pytest.mark.default_timeout(20 * 60)
class TestFullRefresh(BaseTest):
    def assert_emitted_at_increase_on_subsequent_runs(self, first_read_records, second_read_records):
        first_read_records_data = [record.data for record in first_read_records]
        assert first_read_records_data, "At least one record should be read using provided catalog"

        first_read_records_emitted_at = [record.emitted_at for record in first_read_records]
        max_emitted_at_first_read = max(first_read_records_emitted_at)

        second_read_records_emitted_at = [record.emitted_at for record in second_read_records]

        min_emitted_at_second_read = min(second_read_records_emitted_at)

        assert max_emitted_at_first_read < min_emitted_at_second_read, "emitted_at should increase on subsequent runs"

    def assert_two_sequential_reads_produce_same_or_subset_records(
        self, records_1, records_2, configured_catalog, ignored_fields, detailed_logger
    ):
        records_by_stream_1 = defaultdict(list)
        for record in records_1:
            records_by_stream_1[record.stream].append(record.data)

        records_by_stream_2 = defaultdict(list)
        for record in records_2:
            records_by_stream_2[record.stream].append(record.data)

        pks_by_stream = primary_keys_by_stream(configured_catalog)

        for stream in records_by_stream_1:
            if pks_by_stream.get(stream):
                serializer = partial(primary_keys_only, pks=pks_by_stream.get(stream))
            else:
                serializer = partial(make_hashable, exclude_fields=[field.name for field in ignored_fields.get(stream, [])])
            stream_records_1 = records_by_stream_1.get(stream)
            stream_records_2 = records_by_stream_2.get(stream)
            if not set(map(serializer, stream_records_1)).issubset(set(map(serializer, stream_records_2))):
                missing_records = set(map(serializer, stream_records_1)) - (set(map(serializer, stream_records_2)))
                msg = f"{stream}: the two sequential reads should produce either equal set of records or one of them is a strict subset of the other"
                detailed_logger.info(msg)
                detailed_logger.info("First read")
                detailed_logger.log_json_list(stream_records_1)
                detailed_logger.info("Second read")
                detailed_logger.log_json_list(stream_records_2)
                detailed_logger.info("Missing records")
                detailed_logger.log_json_list(missing_records)
                pytest.fail(msg)

    def test_sequential_reads(
        self,
        connector_config: SecretDict,
        configured_catalog: ConfiguredAirbyteCatalog,
        ignored_fields: Optional[Mapping[str, List[IgnoredFieldsConfiguration]]],
        docker_runner: ConnectorRunner,
        detailed_logger: Logger,
    ):
        configured_catalog = full_refresh_only_catalog(configured_catalog)
        output_1 = docker_runner.call_read(connector_config, configured_catalog)
        records_1 = [message.record for message in output_1 if message.type == Type.RECORD]

        # sleep for 1 second to ensure that the emitted_at timestamp is different
        time.sleep(1)

        output_2 = docker_runner.call_read(connector_config, configured_catalog)
        records_2 = [message.record for message in output_2 if message.type == Type.RECORD]

        self.assert_emitted_at_increase_on_subsequent_runs(records_1, records_2)
        self.assert_two_sequential_reads_produce_same_or_subset_records(
            records_1, records_2, configured_catalog, ignored_fields, detailed_logger
        )
