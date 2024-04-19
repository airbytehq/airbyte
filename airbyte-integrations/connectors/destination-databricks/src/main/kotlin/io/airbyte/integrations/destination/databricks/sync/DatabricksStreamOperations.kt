package io.airbyte.integrations.destination.databricks.sync

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.integrations.destination.databricks.jdbc.DatabrickStorageOperations
import io.airbyte.integrations.destination.databricks.staging.DatabricksStagingOperations
import io.airbyte.integrations.destination.sync.StreamOperations
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.stream.Stream

class DatabricksStreamOperations(
    private val sqlOperations: DatabrickStorageOperations,
    private val stagingOperations: DatabricksStagingOperations
) : StreamOperations<MinimumDestinationState.Impl>{
    override fun initialize(destinationInitialStatus: DestinationInitialStatus<MinimumDestinationState.Impl>) {
        sqlOperations.prepare(destinationInitialStatus)
        stagingOperations.create(destinationInitialStatus.streamConfig.id)
    }

    override fun writeRecords(descriptor: StreamDescriptor, stream: Stream<PartialAirbyteMessage>) {
        TODO("Not yet implemented")
    }

    override fun finalizeTable(descriptor: StreamDescriptor, syncSummary: StreamSyncSummary) {
        TODO("Not yet implemented")
    }
}
