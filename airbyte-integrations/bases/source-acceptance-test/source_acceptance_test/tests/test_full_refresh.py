#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from collections import defaultdict
from functools import partial
from logging import Logger
from typing import List, Mapping

import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog, Type
from source_acceptance_test.base import BaseTest
from source_acceptance_test.config import ConnectionTestConfig
from source_acceptance_test.utils import ConnectorRunner, JsonSchemaHelper, SecretDict, full_refresh_only_catalog, make_hashable
from source_acceptance_test.utils.json_schema_helper import CatalogField


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
    def test_sequential_reads(
        self,
        inputs: ConnectionTestConfig,
        connector_config: SecretDict,
        configured_catalog: ConfiguredAirbyteCatalog,
        docker_runner: ConnectorRunner,
        detailed_logger: Logger,
    ):
        ignored_fields = getattr(inputs, "ignored_fields") or {}
        configured_catalog = full_refresh_only_catalog(configured_catalog)
        output = docker_runner.call_read(connector_config, configured_catalog)
        records_1 = [message.record for message in output if message.type == Type.RECORD]
        records_by_stream_1 = defaultdict(list)
        for record in records_1:
            records_by_stream_1[record.stream].append(record.data)

        output = docker_runner.call_read(connector_config, configured_catalog)
        records_2 = [message.record for message in output if message.type == Type.RECORD]
        records_by_stream_2 = defaultdict(list)
        for record in records_2:
            records_by_stream_2[record.stream].append(record.data)

        pks_by_stream = primary_keys_by_stream(configured_catalog)

        for stream in records_by_stream_1:
            if pks_by_stream.get(stream):
                serializer = partial(primary_keys_only, pks=pks_by_stream.get(stream))
            else:
                serializer = partial(make_hashable, exclude_fields=ignored_fields.get(stream))
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
