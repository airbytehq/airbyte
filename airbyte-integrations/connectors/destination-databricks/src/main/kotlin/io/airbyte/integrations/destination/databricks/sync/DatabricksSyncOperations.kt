package io.airbyte.integrations.destination.databricks.sync

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.destination.databricks.typededupe.DatabricksDestinationHandler
import io.airbyte.integrations.destination.sync.SyncOperations
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

class DatabricksSyncOperations(
    private val parsedCatalog: ParsedCatalog,
    private val destinationHandler: DatabricksDestinationHandler
) : SyncOperations {
    override fun initializeStreams() {
        log.info {
            "Preparing required schemas and tables for all streams"
        }
        // What does WriteConfig hold ?
        // streamName = ConfiguredAirbyteStream.AirbyteStream.name / originalName
        // namespace = ConfiguredAirbyteStream.AirbyteStream.namespace / originalNamespace
        // outputSchema = streamId.rawNamespace
        // tmpTableName = namingResolver.getTmpTable (deprecated), // unused from WriteConfig
        // tableName = streamId.rawName
        // syncMode = stream.destinationSyncMode
        // writeDateTime = Instant.now() done once as a static var and passed to all
        val streamsInitialStates = destinationHandler.gatherInitialState(parsedCatalog.streams)

        streamsInitialStates.forEach { it -> it.initialRawTableStatus }
    }

    override fun flushStreams() {
        TODO("Not yet implemented")
    }

    override fun closeStreams(streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary>) {
        TODO("Not yet implemented")
    }
}
