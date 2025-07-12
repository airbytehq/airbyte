#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path

from airbyte_protocol_dataclasses.models import ConfiguredAirbyteStream, DestinationSyncMode
from pytest import fixture
from source_exact import SourceExact
from source_exact.streams import CRMAccountClassificationNames, CRMAccountClassifications

from airbyte_cdk.models import AirbyteCatalog, ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import read


HERE = Path(__file__).parent


@fixture
def config():
    with open(HERE.parent / "secrets/config.json", "r") as file:
        return json.loads(file.read())


@fixture
def configured_catalog(config):
    crmac_stream = CRMAccountClassificationNames(config).as_airbyte_stream()
    crmac_configured = ConfiguredAirbyteStream(
        stream=crmac_stream, sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.overwrite
    )

    return ConfiguredAirbyteCatalog(streams=[crmac_configured])


def test_read_crm_account_classification_names(config, configured_catalog):
    source = SourceExact()
    output = read(source, config, configured_catalog)

    assert len(output.records) > 0
