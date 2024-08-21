/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.operation

import io.airbyte.cdk.integrations.base.JavaBaseConstants.AIRBYTE_META_SYNC_ID_KEY
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.operation.SyncOperation
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil as exceptions
import io.airbyte.commons.concurrency.CompletableFutures.allOf
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil as tdutils
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.CompletableFuture
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.stream.Stream
import org.apache.commons.lang3.concurrent.BasicThreadFactory

class DefaultSyncOperation<DestinationState : MinimumDestinationState>(
    private val parsedCatalog: ParsedCatalog,
    private val destinationHandler: DestinationHandler<DestinationState>,
    private val defaultNamespace: String,
    private val streamOperationFactory: StreamOperationFactory<DestinationState>,
    private val migrations: List<Migration<DestinationState>>,
    private val disableTypeDedupe: Boolean = false,
    private val executorService: ExecutorService =
        Executors.newFixedThreadPool(
            10,
            BasicThreadFactory.Builder().namingPattern("sync-operations-%d").build(),
        )
) : SyncOperation {
    companion object {
        // Use companion to be accessible during instantiation with init
        private val log = KotlinLogging.logger {}
    }

    private val streamOpsMap: Map<StreamId, StreamOperation<DestinationState>>
    init {
        streamOpsMap = createPerStreamOpClients()
    }

    private fun createPerStreamOpClients(): Map<StreamId, StreamOperation<DestinationState>> {
        log.info { "Preparing required schemas and tables for all streams" }
        val streamConfigs = parsedCatalog.streams
        val streamsInitialStates = destinationHandler.gatherInitialState(streamConfigs)

        val postMigrationInitialStates =
            tdutils.executeRawTableMigrations(
                executorService,
                destinationHandler,
                migrations,
                streamsInitialStates
            )
        destinationHandler.commitDestinationStates(
            postMigrationInitialStates.associate { it.streamConfig.id to it.destinationState }
        )

        // Prepare raw and final schemas
        val rawNamespaces = streamConfigs.map { it.id.rawNamespace }.toSet()
        val finalNamespaces = streamConfigs.map { it.id.finalNamespace }.toSet()
        val allNamespaces =
            if (disableTypeDedupe) rawNamespaces else rawNamespaces + finalNamespaces
        destinationHandler.createNamespaces(allNamespaces)

        val initializationFutures =
            postMigrationInitialStates
                .map {
                    CompletableFuture.supplyAsync(
                        {
                            Pair(
                                it.streamConfig.id,
                                streamOperationFactory.createInstance(it, disableTypeDedupe)
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
        destinationHandler.commitDestinationStates(
            futuresResult
                // If we're here, then all the futures were successful, so we're in the Right case
                // of every Either
                .map { it.right!! }
                .associate { (id, streamOps) -> id to streamOps.updatedDestinationState }
        )
        return result.toMap()
    }

    override fun flushStream(descriptor: StreamDescriptor, stream: Stream<PartialAirbyteMessage>) {
        val streamConfig =
            parsedCatalog.getStream(descriptor.namespace ?: defaultNamespace, descriptor.name)
        streamOpsMap[streamConfig.id]?.writeRecords(
            streamConfig,
            stream.map { record ->
                if (record.record!!.meta == null) {
                    record.record!!.meta = AirbyteRecordMessageMeta()
                }
                record.also {
                    it.record!!
                        .meta!!
                        .setAdditionalProperty(
                            AIRBYTE_META_SYNC_ID_KEY,
                            streamConfig.syncId,
                        )
                }
            },
        )
    }

    override fun finalizeStreams(streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary>) {
        try {
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
        } finally {
            log.info { "Cleaning up sync operation thread pools" }
            executorService.shutdown()
        }
    }
}
