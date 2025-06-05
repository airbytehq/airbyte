package io.airbyte.integrations.destination.clickhouse_v2.write

import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.orchestration.db.BaseDatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
class ClickhouseDirectLoadDatabaseInitialStatusGatherer(
    airbyteClient: AirbyteClient,
    clickhouseConfiguration: ClickhouseConfiguration,
    // TODO: Change that; maybe create a bean for it?
    @Named("internalNamespace") internalNamespace: String,
) : BaseDatabaseInitialStatusGatherer<DirectLoadInitialStatus>(
    airbyteClient,
    clickhouseConfiguration.resolvedDatabase,
    internalNamespace,
)
