#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import ConnectorSpecification
from destination_snowflake_cortex.destination import DestinationSnowflakeCortex

def test_spec(self):
    destination = DestinationSnowflakeCortex()
    result = destination.spec()

    self.assertIsInstance(result, ConnectorSpecification)
