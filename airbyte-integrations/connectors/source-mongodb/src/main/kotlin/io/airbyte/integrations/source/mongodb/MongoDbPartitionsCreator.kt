/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import com.mongodb.client.MongoClient
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.read.StreamRecordConsumer
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

/**
 * Creates [MongoDbPartitionReader] instances for a single MongoDB collection stream.
 *
 * For full refresh, this creates one partition reader per stream that reads all documents.
 * If resuming from a previous state, the reader will resume from the last `_id` checkpoint.
 */
class MongoDbPartitionsCreator(
    private val mongoClient: MongoClient,
    private val config: MongoDbSourceConfiguration,
    private val feedBootstrap: StreamFeedBootstrap,
    private val concurrencyResource: ConcurrencyResource,
) : PartitionsCreator {

    private var acquiredThread: ConcurrencyResource.AcquiredThread? = null

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus {
        val acquired = concurrencyResource.tryAcquire()
        if (acquired == null) {
            return PartitionsCreator.TryAcquireResourcesStatus.RETRY_LATER
        }
        acquiredThread = acquired
        return PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run(): List<PartitionReader> {
        val stream: Stream = feedBootstrap.feed
        val currentState: OpaqueStateValue? = feedBootstrap.currentState

        log.info {
            "Creating partitions for stream: ${stream.label}, " +
                "syncMode=${stream.configuredSyncMode}, " +
                "state=${currentState?.toString()?.take(100) ?: "null"}"
        }

        // Check if this stream is already complete
        if (isStreamComplete(currentState)) {
            log.info { "Stream ${stream.label} is already complete, skipping." }
            return emptyList()
        }

        // Determine the lower bound for resumability
        val lowerBound = extractLowerBound(currentState)

        // Get stream record consumers from the feed bootstrap
        val recordConsumers = feedBootstrap.streamRecordConsumers()
        val recordConsumer: StreamRecordConsumer = recordConsumers[stream.id]
            ?: throw IllegalStateException("No record consumer found for stream ${stream.label}")

        val reader = MongoDbPartitionReader(
            mongoClient = mongoClient,
            config = config,
            stream = stream,
            streamRecordConsumer = recordConsumer,
            lowerBound = lowerBound,
            isComplete = false,
        )

        return listOf(reader)
    }

    override fun releaseResources() {
        acquiredThread?.close()
        acquiredThread = null
    }

    /**
     * Checks if the stream has already been fully synced.
     *
     * A stream is complete when:
     * - State is a null JsonNode (signifies completion in the CDK)
     * - State has state_type = "snapshot_completed"
     */
    private fun isStreamComplete(state: OpaqueStateValue?): Boolean {
        if (state == null) return false // No state = cold start
        if (state.isNull) return true // Null node = completed
        val stateType = state.get("state_type")?.asText()
        return stateType == "snapshot_completed"
    }

    /**
     * Extracts the `_id` lower bound from a saved state value for resuming reads.
     */
    private fun extractLowerBound(state: OpaqueStateValue?): String? {
        if (state == null || state.isNull) return null
        val stateType = state.get("state_type")?.asText() ?: return null
        if (stateType == "primary_key") {
            return state.get("id")?.asText()
        }
        return null
    }
}
