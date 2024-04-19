package io.airbyte.integrations.destination.databricks.sync

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.integrations.destination.databricks.sql.SqlOperations
import io.airbyte.integrations.destination.databricks.staging.StagingOperations
import io.airbyte.integrations.destination.sync.StreamOperations
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.stream.Stream

class DatabricksStreamOperations(
    val sqlOperations: SqlOperations<MinimumDestinationState>,
    val stagingOperations: StagingOperations
) : StreamOperations{
    override fun initialize() {
        TODO("Not yet implemented")
    }

    override fun writeRecords(descriptor: StreamDescriptor, stream: Stream<PartialAirbyteMessage>) {
        TODO("Not yet implemented")
    }

    override fun finalizeTable(descriptor: StreamDescriptor, syncSummary: StreamSyncSummary) {
        TODO("Not yet implemented")
    }
}
