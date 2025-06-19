#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import AirbyteCatalog
from airbyte_cdk.test.entrypoint_wrapper import read
from source_exact.streams import CRMAccountClassifications

from source_exact import SourceExact
from pytest import fixture
from pathlib import Path
import json

HERE = Path(__file__).parent


@fixture
def config():
    with open(HERE.parent / "secrets/config.json", "r") as file:
        return json.loads(file.read())

@fixture
def configured_catalog(config):
    ab_stream =[]
    crmac_stream = CRMAccountClassifications(config).as_airbyte_stream()
    ab_stream.append(crmac_stream)
    return AirbyteCatalog(streams=ab_stream)



def test_read_crn_account_classifications(config, configured_catalog):
    source = SourceExact()
    output = source.read()

    # assert len(output) > 1
