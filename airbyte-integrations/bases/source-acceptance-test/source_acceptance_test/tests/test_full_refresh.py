#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import List, Mapping

import pytest
from source_acceptance_test.base import BaseTest
from source_acceptance_test.utils import ConnectorRunner, full_refresh_only_catalog, remove_ignored_fields, serialize


@pytest.mark.default_timeout(20 * 60)
class TestFullRefresh(BaseTest):
    def test_sequential_reads(self, connector_config, configured_catalog, ignored_fields: Mapping[str, List[str]], docker_runner: ConnectorRunner, detailed_logger):
        configured_catalog = full_refresh_only_catalog(configured_catalog)
        output = docker_runner.call_read(connector_config, configured_catalog)
        records_1 = remove_ignored_fields(output, ignored_fields)

        output = docker_runner.call_read(connector_config, configured_catalog)
        records_2 = remove_ignored_fields(output, ignored_fields)

        output_diff = set(map(serialize, records_1)) - set(map(serialize, records_2))
        if output_diff:
            msg = "The two sequential reads should produce either equal set of records or one of them is a strict subset of the other"
            detailed_logger.info(msg)
            detailed_logger.log_json_list(output_diff)
            pytest.fail(msg)
