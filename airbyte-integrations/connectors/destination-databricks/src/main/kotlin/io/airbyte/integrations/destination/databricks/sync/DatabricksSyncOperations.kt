/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.sync

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksDestinationHandler
import io.airbyte.integrations.destination.sync.StreamOperations
import io.airbyte.integrations.destination.sync.SyncOperations
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.stream.Stream

private val log = KotlinLogging.logger {}

class DatabricksSyncOperations(
    private val parsedCatalog: ParsedCatalog,
    private val destinationHandler: DatabricksDestinationHandler,
    private val streamOperations: StreamOperations<MinimumDestinationState.Impl>,
    private val defaultNamespace: String
) : SyncOperations {
    override fun initializeStreams() {
        log.info { "Preparing required schemas and tables for all streams" }
        // Notes for What does WriteConfig hold ?
        // streamName = ConfiguredAirbyteStream.AirbyteStream.name / originalName
        // namespace = ConfiguredAirbyteStream.AirbyteStream.namespace / originalNamespace
        // outputSchema = streamId.rawNamespace
        // tmpTableName = namingResolver.getTmpTable (deprecated), // unused from WriteConfig
        // tableName = streamId.rawName
        // syncMode = stream.destinationSyncMode
        // writeDateTime = Instant.now() done once as a static var and passed to all
        val streamsInitialStates = destinationHandler.gatherInitialState(parsedCatalog.streams)

        // we will commit destinationStates and run Migrations here. For Dbricks we don't need
        // either
        streamsInitialStates.forEach { streamOperations.initialize(it) }
    }

    override fun flushStreams() {
        TODO("Not yet implemented")
    }

    // TODO: This method is an Adapter for FlushFunction, since it operates on per stream basis.
    fun flushStream(descriptor: StreamDescriptor, stream: Stream<PartialAirbyteMessage>) {
        val streamConfig =
            parsedCatalog.getStream(descriptor.namespace ?: defaultNamespace, descriptor.name)
        streamOperations.writeRecords(streamConfig, stream)
    }

    override fun finalizeStreams(streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary>) {
        // Only call finalizeTable operations which has summary. rest will be skipped
        streamSyncSummaries.entries.forEach {
            streamOperations.finalizeTable(
                parsedCatalog.getStream(
                    it.key.namespace ?: defaultNamespace,
                    it.key.name,
                ),
                it.value,
            )
        }
    }
}
