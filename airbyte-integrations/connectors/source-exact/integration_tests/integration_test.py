#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import AirbyteCatalog, SyncMode, ConfiguredAirbyteCatalog
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_protocol_dataclasses.models import ConfiguredAirbyteStream, DestinationSyncMode
from pytest import fixture
from pathlib import Path
import json

from source_exact.streams import CRMAccountClassifications,CRMAccountClassificationNames
from source_exact import SourceExact

HERE = Path(__file__).parent


@fixture
def config():
    with open(HERE.parent / "secrets/config.json", "r") as file:
        return json.loads(file.read())


@fixture
def configured_catalog(config):
    crmac_stream = CRMAccountClassificationNames(config).as_airbyte_stream()
    configured_stream = ConfiguredAirbyteStream(
        stream=crmac_stream,
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.overwrite
    )

    return ConfiguredAirbyteCatalog(streams=[configured_stream])


def test_read_crm_account_classification_names(config, configured_catalog):
    source = SourceExact()
    output = read(source, config, configured_catalog)

    assert len(output.records) > 0
