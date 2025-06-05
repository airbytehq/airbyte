package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.orchestration.db.BaseDatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration

class ClickhouseDirectLoadDatabaseInitialStatusGatherer(
    airbyteClient: AirbyteClient,
    clickhouseConfiguration: ClickhouseConfiguration,
    // TODO: Change that; maybe create a bean for it?
    internalTableDataset: String = "default",
) : BaseDatabaseInitialStatusGatherer<DirectLoadInitialStatus>(
    airbyteClient,
    clickhouseConfiguration.resolvedDatabase,
    internalTableDataset,
)
