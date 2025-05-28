package io.airbyte.integrations.destination.clickhouse_v2.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DefaultDirectLoadTableSqlOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import jakarta.inject.Singleton

class ClickhouseStreamLoader(
    override val stream: DestinationStream
) : StreamLoader {

    override suspend fun start() {
        // Implementation for starting the stream loader
        // TODO: Implement
    }
}

@Singleton
class ClickhouseWriter(private val defaultOperations: DefaultDirectLoadTableSqlOperations,): DirectLoadTableSqlOperations by defaultOperations {
}
