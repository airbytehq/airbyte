/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.Stream
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicReference

/** [PartitionsCreator] implementation for CDC with Debezium. */
class CdcPartitionsCreator<T : Comparable<T>>(
    val concurrencyResource: ConcurrencyResource,
    val feedBootstrap: GlobalFeedBootstrap,
    val creatorOps: CdcPartitionsCreatorDebeziumOperations<T>,
    val readerOps: CdcPartitionReaderDebeziumOperations<T>,
    val lowerBoundReference: AtomicReference<T>,
    val upperBoundReference: AtomicReference<T>,
    val resetReason: AtomicReference<String?>,
) : PartitionsCreator {
    private val log = KotlinLogging.logger {}
    private val acquiredThread = AtomicReference<ConcurrencyResource.AcquiredThread>()

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus {
        val acquiredThread: ConcurrencyResource.AcquiredThread =
            concurrencyResource.tryAcquire()
                ?: return PartitionsCreator.TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredThread.set(acquiredThread)
        return PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override fun releaseResources() {
        acquiredThread.getAndSet(null)?.close()
    }

    override suspend fun run(): List<PartitionReader> {
        resetReason.get()?.let { reason: String ->
            throw TransientErrorException(
                "Triggering reset. Incumbent CDC state is invalid, reason: ${reason}."
            )
        }
        var allStreams: List<Stream> = feedBootstrap.feed.streams
        val activeStreams: List<Stream> by lazy {
            feedBootstrap.feed.streams.filter { feedBootstrap.currentState(it) != null }
        }
        val syntheticOffset: DebeziumOffset by lazy { creatorOps.generateColdStartOffset() }
        // Ensure that the WAL position upper bound has been computed for this sync.
        val upperBound: T =
            upperBoundReference.updateAndGet { it ?: creatorOps.position(syntheticOffset) }
        // Deserialize the incumbent state value, if it exists.
        val warmStartState: DebeziumWarmStartState? =
            feedBootstrap.currentState?.let {
                try {
                    creatorOps.deserializeState(it)
                } catch (e: Exception) {
                    // This catch should be redundant for well-behaved implementations
                    // but is included anyway for safety.
                    AbortDebeziumWarmStartState(e.toString())
                }
            }
        val debeziumProperties: Map<String, String>
        val startingOffset: DebeziumOffset
        val startingSchemaHistory: DebeziumSchemaHistory?
        when (warmStartState) {
            null -> {
                debeziumProperties = creatorOps.generateColdStartProperties(allStreams)
                startingOffset = syntheticOffset
                startingSchemaHistory = null
            }
            is ValidDebeziumWarmStartState -> {
                debeziumProperties = creatorOps.generateWarmStartProperties(activeStreams)
                startingOffset = warmStartState.offset
                startingSchemaHistory = warmStartState.schemaHistory
            }
            is AbortDebeziumWarmStartState -> {
                val e =
                    ConfigErrorException(
                        "Incumbent CDC state is invalid, reason: ${warmStartState.reason}"
                    )
                log.error(e) { "Aborting. ${e.message}." }
                throw e
            }
            is ResetDebeziumWarmStartState -> {
                // The incumbent CDC state value is invalid and the sync needs to be reset.
                // Doing so is not so straightforward as throwing a TransientErrorException because
                // a STATE message with a post-reset state needs to be emitted first.
                // This new state is obtained by zeroing all corresponding feeds in the StateManager
                // and returning a CdcPartitionReader for a cold start with a synthetic offset.
                // This CdcPartitionReader will run, after which the desired STATE message will be
                // emitted, and finally the next CdcPartitionsCreator will throw a
                // TransientErrorException. The next sync will then snapshot the tables.
                resetReason.set(warmStartState.reason)
                log.info { "Resetting invalid incumbent CDC state with synthetic state." }
                feedBootstrap.resetAll()
                debeziumProperties = creatorOps.generateColdStartProperties(allStreams)
                startingOffset = syntheticOffset
                startingSchemaHistory = null
            }
        }
        // Build and return PartitionReader instance, if applicable.
        val partitionReader =
            CdcPartitionReader(
                concurrencyResource,
                feedBootstrap.streamRecordConsumers(),
                readerOps,
                upperBound,
                debeziumProperties,
                startingOffset,
                startingSchemaHistory,
                warmStartState !is ValidDebeziumWarmStartState,
            )
        val lowerBound: T = creatorOps.position(startingOffset)
        val lowerBoundInPreviousRound: T? = lowerBoundReference.getAndSet(lowerBound)
        if (partitionReader.isInputStateSynthetic) {
            // Handle synthetic offset edge-case, which always needs to run.
            // Debezium needs to run to generate the full state, which might include schema history.
            log.info { "Current offset is synthetic." }
            return listOf(partitionReader)
        }
        if (upperBound <= lowerBound) {
            // Handle completion due to reaching the WAL position upper bound.
            log.info {
                "Current position '$lowerBound' equals or exceeds target position '$upperBound'."
            }
            return emptyList()
        }
        if (lowerBoundInPreviousRound != null && lowerBound <= lowerBoundInPreviousRound) {
            // Handle completion due to stalling.
            log.info {
                "Current position '$lowerBound' has not increased in the last round, " +
                    "prior to which is was '$lowerBoundInPreviousRound'."
            }
            return emptyList()
        }
        // Handle common case.
        log.info { "Current position '$lowerBound' does not exceed target position '$upperBound'." }
        return listOf(partitionReader)
    }
}
