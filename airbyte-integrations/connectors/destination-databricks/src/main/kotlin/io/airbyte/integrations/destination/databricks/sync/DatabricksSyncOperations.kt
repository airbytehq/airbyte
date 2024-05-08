/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.sync

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil as exceptions
import io.airbyte.commons.concurrency.CompletableFutures.allOf
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksDestinationHandler
import io.airbyte.integrations.destination.sync.StorageOperations
import io.airbyte.integrations.destination.sync.SyncOperations
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.CompletableFuture
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.stream.Stream
import org.apache.commons.lang3.concurrent.BasicThreadFactory

class DatabricksSyncOperations(
    private val parsedCatalog: ParsedCatalog,
    private val destinationHandler: DatabricksDestinationHandler,
    private val defaultNamespace: String,
    private val storageOperations: StorageOperations,
    private val fileUploadFormat: FileUploadFormat,
    private val executorService: ExecutorService =
        Executors.newFixedThreadPool(
            10,
            BasicThreadFactory.Builder().namingPattern("sync-operations-%d").build(),
        )
) : SyncOperations {
    companion object {
        // Use companion to be accessible during instantiation with init
        private val log = KotlinLogging.logger {}
    }

    private val streamOpsMap: Map<StreamId, DatabricksStreamOperations>
    init {
        streamOpsMap = createPerStreamOpClients()
    }

    private fun createPerStreamOpClients(): Map<StreamId, DatabricksStreamOperations> {
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
        val initializationFutures =
            streamsInitialStates
                .map {
                    CompletableFuture.supplyAsync(
                        {
                            Pair(
                                it.streamConfig.id,
                                DatabricksStreamOperations(storageOperations, fileUploadFormat, it)
                            )
                        },
                        executorService,
                    )
                }
                .toList()
        val futuresResult = allOf(initializationFutures).toCompletableFuture().get()
        val result =
            exceptions.getResultsOrLogAndThrowFirst(
                "Following exceptions occurred during sync initialization",
                futuresResult,
            )
        return result.toMap()
    }

    override fun flushStream(descriptor: StreamDescriptor, stream: Stream<PartialAirbyteMessage>) {
        val streamConfig =
            parsedCatalog.getStream(descriptor.namespace ?: defaultNamespace, descriptor.name)
        streamOpsMap[streamConfig.id]?.writeRecords(streamConfig, stream)
    }

    override fun finalizeStreams(streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary>) {
        // Only call finalizeTable operations which has summary. rest will be skipped
        val finalizeFutures =
            streamSyncSummaries.entries
                .map {
                    CompletableFuture.supplyAsync(
                        {
                            val streamConfig =
                                parsedCatalog.getStream(
                                    it.key.namespace ?: defaultNamespace,
                                    it.key.name,
                                )
                            streamOpsMap[streamConfig.id]?.finalizeTable(streamConfig, it.value)
                        },
                        executorService,
                    )
                }
                .toList()
        val futuresResult = allOf(finalizeFutures).toCompletableFuture().join()
        exceptions.getResultsOrLogAndThrowFirst(
            "Following exceptions occurred while finalizing the sync",
            futuresResult,
        )
        log.info { "Cleaning up sync operation thread pools" }
        executorService.shutdown()
    }
}
