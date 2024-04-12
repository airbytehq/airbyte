#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, List, Mapping, Optional

from airbyte_cdk.models import ConfiguredAirbyteCatalog, DestinationSyncMode
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog
from destination_snowflake_cortex.client import SnowflakeCortexClient
from typing import Any, Iterable, Mapping



class SnowflakeCortexWriter:

    def __init__(
        self,
        client: SnowflakeCortexClient,
    ):
        self.client = client


    def write(self, configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]) -> Iterable[AirbyteMessage]:
        # to-do: transfrom the data into documents 
        # to-do: write the documents to the destination
        self.client.write(configured_catalog, input_messages)