#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.connector import TConfig
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.source import TCatalog, TState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_protocol.models import AirbyteCatalog, AirbyteConnectionStatus, AirbyteMessage, Status, SyncMode
from unit_tests.sources.file_based.scenarios.scenario_builder import SourceProvider, TestScenarioBuilder


class TestSource(Source):

    def read(self, logger: logging.Logger, config: TConfig, catalog: TCatalog, state: TState = None) -> Iterable[AirbyteMessage]:
        pass

    def discover(self, logger: logging.Logger, config: TConfig) -> AirbyteCatalog:
        pass

    def check(self, logger: logging.Logger, config: TConfig) -> AirbyteConnectionStatus:
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)



_base_success_scenario = (
    TestScenarioBuilder(lambda x: SourceProvider(TestSource()))
    .set_config(
        {
        }
    )
    .set_expected_check_status("SUCCEEDED")
)

test_source_base_scenario = (_base_success_scenario.copy()
    .set_name("test_source_base_scenario")
    .build())
